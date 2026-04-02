"""Extract product highlights using Claude API."""
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


SYSTEM_PROMPT = """你是一位專業的產品文案顧問。
根據使用者提供的商品資料，提取 5-8 個最重要的產品亮點。

回傳格式必須是 JSON 陣列，每個項目包含：
- title: 亮點標題（6-15 字，簡潔有力）
- explanation: 說明（2-3 句話，說明為何這是亮點、對使用者的價值）

如果商品資料不足以產生 5 個亮點，盡量提取所有可用的亮點（最少 1 個）。

只回傳 JSON 陣列，不要有其他文字。"""


async def extract_highlights(product: dict) -> list[dict]:
    """Call Claude API and return list of highlight dicts."""
    client = _get_client()

    user_content = f"""商品名稱：{product.get('name', '')}
商品描述：{product.get('description', '')}
價格：{product.get('price', '')}"""

    message = await asyncio.to_thread(
        client.messages.create,
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        highlights = json.loads(raw)
        if isinstance(highlights, list):
            return highlights
    except json.JSONDecodeError:
        pass

    return [{"title": "商品亮點", "explanation": product.get("description", "")[:200]}]
