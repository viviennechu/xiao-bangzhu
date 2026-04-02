"""Generate social media posts (IG / FB / LINE) in 大V's voice."""
import asyncio
import json
import os

import anthropic

from ai.persona import BIGV_PERSONA

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


_SYSTEM_PROMPT = f"""你是大V，請完全代入她的身份寫社群短文。
{BIGV_PERSONA}
格式規則：
- IG：≤300 字，結尾 5–8 個 #hashtag，hashtag 可夾在文中，不全堆到最後
- FB：≤300 字，對話感強，輕鬆分享語氣
- LINE：≤200 字，直接、有行動呼籲

輸出格式（JSON）：
{
  "ig_post": "IG 貼文內容",
  "fb_post": "FB 貼文內容",
  "line_post": "LINE 群組貼文內容"
}"""


async def generate_social(
    product: dict,
    highlights: list[dict],
    price_result: dict | None,
    competitor_comparison: dict | None,
) -> dict:
    """Generate IG, FB, and LINE posts in a single call.

    Returns:
        {"ig_post": str, "fb_post": str, "line_post": str}
    """
    client = _get_client()

    highlights_text = "\n".join(
        f"- {h.get('title', '')}: {h.get('explanation', '')}" for h in highlights[:5]
    )

    price_advantage = ""
    if competitor_comparison and competitor_comparison.get("is_competitive") is True:
        diff = competitor_comparison.get("difference_amount", 0)
        price_advantage = f"\n💡 比市面同類團購便宜約 {diff} 元，可在文案中強調。"
    elif price_result and not price_result.get("is_warning"):
        price_advantage = (
            f"\n💡 團購價 {price_result['group_buy_price']} 元，"
            f"比市售便宜 {price_result['savings_amount']} 元（{price_result['savings_percent']}%）。"
        )

    user_content = f"""請幫我寫三種平台的社群短文：

商品：{product.get('name', '')}
亮點：
{highlights_text}
{price_advantage}

請輸出 JSON 格式（ig_post、fb_post、line_post 三個欄位）。"""

    message = await asyncio.to_thread(
        client.messages.create,
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw = message.content[0].text.strip()

    try:
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except (json.JSONDecodeError, IndexError):
        return {"ig_post": raw, "fb_post": raw, "line_post": raw}
