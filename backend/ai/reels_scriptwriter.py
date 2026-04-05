"""Generate Reels scripts in 大V's casual, relatable style."""
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


_SYSTEM_PROMPT = f"""你是大V，請完全代入她的身份寫 Instagram Reels 腳本。
{BIGV_PERSONA}
腳本規則：
- 不說教、不完美、真實感
- 說話像朋友分享，不是在上課
- 教養/教育類商品：至少說一句「我自己也做不到 100%」或類似的承認
- 蒙特梭利概念用口語說，不用術語上課
- 整體風格參考：鷹式一家（生活化）、思誼職能治療師（輕鬆解決小問題）

輸出格式（JSON）：
{{
  "hook": "開場白（≤15字，問句或反常識）",
  "segments": [
    {{
      "voiceover": "旁白文字",
      "screen_hint": "畫面提示（拍什麼）"
    }}
  ],
  "cta": "結尾行動呼籲（≤10字）"
}}

segments 必須 3–5 個。"""


async def generate_reels(
    product: dict,
    highlights: list[dict],
    ami_snippet: str | None,
    product_category: str = "general",
) -> dict:
    """Generate a Reels script.

    Returns:
        {"hook": str, "segments": list[dict], "cta": str}
    """
    client = _get_client()

    highlights_text = "\n".join(
        f"- {h.get('title', '')}: {h.get('explanation', '')}" for h in highlights[:5]
    )

    is_educational = any(kw in (product_category or "").lower()
                         for kw in ("educational", "books", "toys", "蒙特梭利", "早教", "童書", "教具"))

    ami_block = ""
    if ami_snippet and is_educational:
        ami_block = f"""
【蒙特梭利理論依據 — 請自然融入其中一個 segment】
{ami_snippet}
"""

    user_content = f"""請幫我寫一支 Reels 腳本：

商品：{product.get('name', '')}
分類：{product_category}
亮點：
{highlights_text}
{ami_block}
要求：
- Hook 用問句或反常識開場
- 3–5 個 segments，各有旁白和畫面提示
- 教養類商品要有「我自己也沒做到 100%」的真實感
- 結尾 CTA

請輸出 JSON 格式（hook、segments、cta 三個欄位）。"""

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
        result = json.loads(raw)
        # Clamp segments to 3–5
        segs = result.get("segments", [])
        result["segments"] = segs[:5] if len(segs) > 5 else segs
        return result
    except (json.JSONDecodeError, IndexError):
        return {"hook": "", "segments": [], "cta": "", "raw": raw}
