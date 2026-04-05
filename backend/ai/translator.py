"""大V翻譯機 — 把助理草稿改寫成大V或WA宇宸的口吻，輸出三種格式。"""
import asyncio
import json
import os

import anthropic

from ai.persona import BIGV_PERSONA
from ai.wa_persona import WA_PERSONA

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


_BIGV_SYSTEM = f"""你是大V，把助理寫的草稿改寫成完全屬於你的聲音。
{BIGV_PERSONA}

## 改寫原則

- 資訊要保留，口吻要換掉
- 不能有AI感：不能有條列式小標、不能有🔸🔹這種符號、不能有「以下為您整理」
- 段落流動，短句打頭，信息藏在對話裡
- hashtag 夾在文中段落結尾，不全堆到最後
- 2022年前的寫法：沒有結構感，像在說話，不像在寫報告
- 結尾不要每次都用「跟不跟團我都一樣愛你們」，要換著說或留白
"""

_WA_SYSTEM = f"""你是宇宸（WA），把助理寫的草稿改寫成你自己的口吻。
{WA_PERSONA}

## 改寫原則

- 大幅濃縮：草稿多長，你的版本就要短很多
- 只留重點：自己用過的感受、孩子穗穗的反應、老公（大廚）的判斷
- 不說教、不長篇、不熱情
- 結尾直接或用 🍵 收，不要客套
"""


def _build_prompt(draft: str, output_format: str) -> str:
    format_instructions = {
        "blog": """請輸出 FB 長文 / Blog 文章格式（JSON）：
{
  "title": "文章標題",
  "content": "完整文章內容（Markdown）"
}""",

        "ig_stories": """請輸出 IG 限時動態腳本（JSON），7–9 張：
{
  "slides": [
    {
      "index": 1,
      "purpose": "這張的目的（開場/知識點/產品/金句/CTA）",
      "text": "畫面上的文字（≤40字）",
      "visual": "視覺建議"
    }
  ]
}""",

        "group_fire": """請輸出 LINE 群組生火文（JSON），短、直接、有行動呼籲：
{
  "content": "群組貼文內容（≤150字）"
}""",
    }

    return f"""以下是助理寫的草稿，請改寫成你的口吻：

【草稿】
{draft}

【輸出格式】
{format_instructions.get(output_format, format_instructions['blog'])}

請直接輸出 JSON，不要加任何說明文字。"""


async def translate(
    draft: str,
    persona: str,
    output_format: str,
) -> dict:
    """把草稿改寫成指定人設的指定格式。

    Args:
        draft: 助理寫的原始草稿
        persona: "bigv" 或 "wa"
        output_format: "blog" | "ig_stories" | "group_fire"

    Returns:
        dict，結構依 output_format 而定
    """
    client = _get_client()
    system = _BIGV_SYSTEM if persona == "bigv" else _WA_SYSTEM
    user_content = _build_prompt(draft, output_format)

    message = await asyncio.to_thread(
        client.messages.create,
        model="claude-3-5-sonnet-20241022",
        max_tokens=3000,
        system=system,
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
        return {"content": raw}
