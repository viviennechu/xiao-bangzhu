"""Market analysis — Google Trends + IG social signal + marketing recommendations."""
import logging
import re
import time

import requests

logger = logging.getLogger(__name__)

EDUCATIONAL_CATEGORIES = {"educational", "education", "books", "book", "toys", "toy", "蒙特梭利", "早教", "童書", "教具"}


# ── Google Trends ──────────────────────────────────────────────────────────────

def _fetch_trends(keyword: str) -> dict | None:
    """Fetch 12-month Google Trends data. Returns trend_direction and avg_score or None on failure."""
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="zh-TW", tz=480, timeout=(10, 25))
        pytrends.build_payload([keyword], timeframe="today 12-m", geo="TW")
        data = pytrends.interest_over_time()

        if data.empty or keyword not in data.columns:
            return None

        values = data[keyword].tolist()
        if not values:
            return None

        avg_3m = sum(values[-13:]) / min(len(values), 13) if len(values) >= 4 else sum(values) / len(values)
        avg_full = sum(values) / len(values)

        last_4w = values[-5:] if len(values) >= 5 else values
        avg_last_4w = sum(last_4w) / len(last_4w)

        if avg_last_4w >= avg_3m + 10:
            direction = "rising"
        elif avg_last_4w <= avg_3m - 10:
            direction = "declining"
        else:
            direction = "stable"

        return {"trend_direction": direction, "avg_score": round(avg_3m, 1)}

    except Exception as exc:
        logger.warning("Google Trends fetch failed for '%s': %s", keyword, exc)
        return None


# ── IG hashtag signal ──────────────────────────────────────────────────────────

def _fetch_ig_signal(keyword: str) -> str | None:
    """Estimate IG competition level from hashtag post count. Returns 'high'/'low'/None."""
    hashtag = keyword.replace(" ", "").replace("#", "")
    url = f"https://www.instagram.com/explore/tags/{hashtag}/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None

        match = re.search(r'"edge_hashtag_to_media".*?"count":\s*(\d+)', resp.text)
        if not match:
            return None

        count = int(match.group(1))
        if count >= 100000:
            return "high"
        elif count < 10000:
            return "low"
        else:
            return "medium"

    except Exception as exc:
        logger.warning("IG signal fetch failed for '%s': %s", hashtag, exc)
        return None


# ── Strategy classification ────────────────────────────────────────────────────

def _classify_strategy(product_category: str, competitor_price_data: dict | None) -> str:
    cat_lower = (product_category or "").lower()

    if any(kw in cat_lower for kw in EDUCATIONAL_CATEGORIES):
        return "montessori-knowledge"

    if (
        competitor_price_data
        and competitor_price_data.get("is_competitive") is True
    ):
        return "price-value"

    return "lifestyle-experience"


# ── Marketing recommendation ───────────────────────────────────────────────────

def _build_recommendation(
    trend_direction: str | None,
    social_competition: str | None,
    strategy_type: str,
) -> dict:
    all_formats = ["blog", "social", "reels"]

    if trend_direction is None and social_competition is None:
        return {
            "recommended_formats": all_formats,
            "primary_platform": "blog",
            "strategy_type": strategy_type,
        }

    if trend_direction == "rising" and social_competition == "low":
        return {
            "recommended_formats": all_formats,
            "primary_platform": "blog",
            "strategy_type": strategy_type,
        }

    if trend_direction == "rising" and social_competition in ("high", "medium"):
        return {
            "recommended_formats": ["social", "reels"],
            "primary_platform": "social",
            "strategy_type": "short-hit",
        }

    if trend_direction == "stable":
        return {
            "recommended_formats": ["social", "reels"],
            "primary_platform": "social",
            "strategy_type": strategy_type,
        }

    # declining or unknown
    return {
        "recommended_formats": all_formats,
        "primary_platform": "blog",
        "strategy_type": strategy_type,
    }


# ── Public API ─────────────────────────────────────────────────────────────────

def analyze_market(
    keyword: str,
    product_category: str = "general",
    competitor_price_data: dict | None = None,
) -> dict:
    """Run market analysis for a product keyword.

    Returns:
        {
            "trend_direction": "rising" | "stable" | "declining" | None,
            "avg_score": float | None,
            "social_competition": "high" | "medium" | "low" | None,
            "strategy_type": str,
            "recommended_formats": list[str],
            "primary_platform": str,
        }
    """
    trends = _fetch_trends(keyword)
    social = _fetch_ig_signal(keyword)
    strategy = _classify_strategy(product_category, competitor_price_data)

    trend_direction = trends["trend_direction"] if trends else None
    avg_score = trends["avg_score"] if trends else None

    recommendation = _build_recommendation(trend_direction, social, strategy)

    return {
        "trend_direction": trend_direction,
        "avg_score": avg_score,
        "social_competition": social,
        **recommendation,
    }
