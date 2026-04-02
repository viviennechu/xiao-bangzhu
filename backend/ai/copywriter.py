"""Copywriter orchestration layer — runs blog, social, reels writers in parallel."""
import asyncio
import os

import anthropic

from ai.blog_writer import generate_blog
from ai.social_writer import generate_social
from ai.reels_scriptwriter import generate_reels
from ai.style_loader import load_style_examples
from knowledge.ami_index import get_ami_snippet


def _detect_category(product: dict) -> str:
    """Infer product category from name/description for AMI injection decisions."""
    name = (product.get("name", "") + " " + product.get("description", "")).lower()
    educational_keywords = ["書", "繪本", "教具", "蒙特梭利", "早教", "益智", "學習", "積木", "puzzle"]
    if any(kw in name for kw in educational_keywords):
        return "educational"
    return "general"


def _assemble_context(
    product: dict,
    highlights: list[dict],
    price_result: dict | None,
    market_analysis: dict | None,
    competitor_comparison: dict | None,
) -> dict:
    """Assemble shared context package for all three writers."""
    product_name = product.get("name", "")
    category = _detect_category(product)

    style_examples = load_style_examples(
        n=3,
        topic=product_name,
        category_filter="蒙特梭利" if category == "educational" else None,
    )

    ami_snippet = get_ami_snippet(product_name) if category == "educational" else None

    return {
        "product": product,
        "highlights": highlights,
        "price_result": price_result,
        "market_analysis": market_analysis,
        "competitor_comparison": competitor_comparison,
        "ami_snippet": ami_snippet,
        "style_examples": style_examples,
        "product_category": category,
    }


async def generate_all(
    product: dict,
    highlights: list[dict],
    price_result: dict | None = None,
    market_analysis: dict | None = None,
    competitor_comparison: dict | None = None,
) -> dict:
    """Generate blog, social, and reels outputs in parallel.

    Returns:
        {
            "blog": {"title", "meta_description", "content"} | None,
            "social": {"ig_post", "fb_post", "line_post"} | None,
            "reels": {"hook", "segments", "cta"} | None,
            "errors": {writer: error_message},
        }
    """
    ctx = _assemble_context(product, highlights, price_result, market_analysis, competitor_comparison)

    async def safe_blog():
        try:
            return await generate_blog(
                product=ctx["product"],
                highlights=ctx["highlights"],
                price_result=ctx["price_result"],
                style_examples=ctx["style_examples"],
                ami_snippet=ctx["ami_snippet"],
                product_category=ctx["product_category"],
            )
        except Exception as exc:
            return {"_error": str(exc)}

    async def safe_social():
        try:
            return await generate_social(
                product=ctx["product"],
                highlights=ctx["highlights"],
                price_result=ctx["price_result"],
                competitor_comparison=ctx["competitor_comparison"],
            )
        except Exception as exc:
            return {"_error": str(exc)}

    async def safe_reels():
        try:
            return await generate_reels(
                product=ctx["product"],
                highlights=ctx["highlights"],
                ami_snippet=ctx["ami_snippet"],
                product_category=ctx["product_category"],
            )
        except Exception as exc:
            return {"_error": str(exc)}

    blog_result, social_result, reels_result = await asyncio.gather(
        safe_blog(), safe_social(), safe_reels()
    )

    errors = {}
    if isinstance(blog_result, dict) and "_error" in blog_result:
        errors["blog"] = blog_result["_error"]
        blog_result = None
    if isinstance(social_result, dict) and "_error" in social_result:
        errors["social"] = social_result["_error"]
        social_result = None
    if isinstance(reels_result, dict) and "_error" in reels_result:
        errors["reels"] = reels_result["_error"]
        reels_result = None

    return {
        "blog": blog_result,
        "social": social_result,
        "reels": reels_result,
        "errors": errors,
    }


# Backward compat: old callers that use generate_copy (LINE only)
async def generate_copy(product: dict, highlights: list[dict], price_result: dict | None = None) -> str:
    result = await generate_all(product=product, highlights=highlights, price_result=price_result)
    social = result.get("social") or {}
    return social.get("line_post", "（無法生成文案）")
