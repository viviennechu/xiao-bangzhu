"""Generate SEO blog posts in 大V's writing style."""
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


def _build_system_prompt(style_examples: list[str], ami_snippet: str | None) -> str:
    examples_block = "\n\n---\n\n".join(
        f"【範例 {i+1}】\n{ex}" for i, ex in enumerate(style_examples)
    ) if style_examples else "（無範例）"

    ami_block = ""
    if ami_snippet:
        ami_block = f"""
以下是蒙特梭利理論依據，如果商品與早教/教育/育兒相關，請自然地融入文章內容：

【蒙特梭利理論依據】
{ami_snippet}
"""

    return f"""你是大V，請完全代入她的身份寫 SEO 部落格文章。
{BIGV_PERSONA}
以下是她過去的文章範例，請學習語氣和結構：

{examples_block}
{ami_block}
寫文規則：
1. 開頭從個人生活場景或育兒問題切入，不直接說商品名
2. 段落短、換行多、製造呼吸感
3. 教育類商品自然融入蒙特梭利觀念，用口語說，不用術語上課
4. 「大V老實說」段落誠實說優缺點（有時說小缺點反而更可信）
5. 結尾用 #hashtag（4–6 個），夾在文中而非全堆到最後
6. 用具體的亮亮、好好、Mumu 舉例，不要只說「孩子」

輸出格式（JSON）：
{{
  "title": "SEO 標題（含主要關鍵字）",
  "meta_description": "120–160 字的 meta description",
  "content": "完整文章（Markdown 格式，含 # H1 和 ## H2）"
}}"""


async def generate_blog(
    product: dict,
    highlights: list[dict],
    price_result: dict | None,
    style_examples: list[str],
    ami_snippet: str | None,
    product_category: str = "general",
) -> dict:
    """Generate an SEO blog post.

    Returns:
        {"title": str, "meta_description": str, "content": str}
    """
    client = _get_client()
    system_prompt = _build_system_prompt(style_examples, ami_snippet)

    highlights_text = "\n".join(
        f"- {h.get('title', '')}: {h.get('explanation', '')}" for h in highlights
    )

    price_section = ""
    if price_result:
        if price_result.get("is_warning"):
            price_section = f"\n（價格資訊僅供參考，不在文章中強調）"
        else:
            price_section = (
                f"\n團購價：{price_result['group_buy_price']} 元"
                f"，市售價：{price_result['retail_price']} 元"
                f"，省 {price_result['savings_amount']} 元（{price_result['savings_percent']}%）"
            )

    is_educational = any(kw in (product_category or "").lower()
                         for kw in ("educational", "books", "toys", "蒙特梭利", "早教", "童書", "教具"))

    ami_instruction = ""
    if ami_snippet and is_educational:
        ami_instruction = "\n請在文章中自然融入「蒙特梭利理論依據」區塊提供的知識，並標明出處。"

    user_content = f"""請幫我寫一篇 SEO 部落格文章：

商品名稱：{product.get('name', '')}
商品分類：{product_category}
{price_section}

主要亮點：
{highlights_text}
{ami_instruction}

文章結構要求：
1. H1 標題含主要關鍵字
2. 個人化開場（從生活場景切入）
3. 至少 3 個 H2 段落，依亮點展開
4. 「大V老實說」誠實說優缺點
5. 若有價格優惠，加入比較段落
6. 4–6 個 hashtag 收尾

請以 JSON 格式輸出（title、meta_description、content 三個欄位）。"""

    message = await asyncio.to_thread(
        client.messages.create,
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )

    raw = message.content[0].text.strip()

    # Parse JSON output
    try:
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except (json.JSONDecodeError, IndexError):
        return {
            "title": product.get("name", "商品推薦"),
            "meta_description": "",
            "content": raw,
        }
