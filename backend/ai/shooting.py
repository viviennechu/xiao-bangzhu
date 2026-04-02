"""Generate photo/video shooting plan from product highlights using Claude API."""
import asyncio
import json
import os
import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


SYSTEM_PROMPT = """你是一位專業的電商內容攝影顧問。
根據使用者提供的商品亮點，產生一份完整的拍攝清單。

回傳格式必須是 JSON 物件，包含兩個陣列：
- photos: 照片拍攝建議，每項包含 { "shot": "拍攝描述", "highlight": "對應亮點標題" }
- videos: 影片拍攝建議，每項包含 { "shot": "拍攝描述", "highlight": "對應亮點標題" }

照片至少 3 張，影片至少 2 支。
照片建議：包裝正面、細節特寫、使用情境、比較尺寸等。
影片建議：開箱過程、使用示範、效果展示等。

只回傳 JSON 物件，不要有其他文字。"""


async def generate_shooting_plan(highlights: list[dict]) -> dict:
    """Return shooting plan dict with 'photos' and 'videos' arrays."""
    client = _get_client()

    highlights_text = "\n".join(
        f"- {h.get('title', '')}: {h.get('explanation', '')}"
        for h in highlights
    )

    message = await asyncio.to_thread(
        client.messages.create,
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"商品亮點：\n{highlights_text}"}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        plan = json.loads(raw)
        if isinstance(plan, dict) and "photos" in plan and "videos" in plan:
            return plan
    except json.JSONDecodeError:
        pass

    # Fallback
    return {
        "photos": [{"shot": "商品正面拍攝", "highlight": ""}, {"shot": "細節特寫", "highlight": ""}, {"shot": "使用情境", "highlight": ""}],
        "videos": [{"shot": "開箱影片", "highlight": ""}, {"shot": "使用示範", "highlight": ""}],
    }
