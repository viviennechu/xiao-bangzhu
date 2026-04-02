"""Competitor price lookup — search chienchien99 historical group buy prices."""
import logging
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "competitor_prices.db"
CACHE_TTL_DAYS = 7
COMPETITOR_FB_PAGE = "site:facebook.com/chienchien99"


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS competitor_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_keyword TEXT NOT NULL,
            competitor_price INTEGER,
            source_snippet TEXT,
            searched_at TEXT NOT NULL
        )
    """)
    conn.commit()


def _get_cached(keyword: str) -> dict | None:
    """Return cached result if fresh (within CACHE_TTL_DAYS), else None."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            _init_db(conn)
            cutoff = (datetime.now() - timedelta(days=CACHE_TTL_DAYS)).isoformat()
            row = conn.execute(
                "SELECT competitor_price, source_snippet FROM competitor_prices "
                "WHERE product_keyword = ? AND searched_at > ? ORDER BY searched_at DESC LIMIT 1",
                (keyword, cutoff),
            ).fetchone()
            if row:
                return {"competitor_price": row[0], "source_snippet": row[1]}
    except Exception as exc:
        logger.warning("Cache read failed: %s", exc)
    return None


def _save_cache(keyword: str, price: int | None, snippet: str) -> None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            _init_db(conn)
            conn.execute(
                "INSERT INTO competitor_prices (product_keyword, competitor_price, source_snippet, searched_at) "
                "VALUES (?, ?, ?, ?)",
                (keyword, price, snippet, datetime.now().isoformat()),
            )
            conn.commit()
    except Exception as exc:
        logger.warning("Cache write failed: %s", exc)


def _extract_price(text: str) -> int | None:
    """Extract the lowest NTD price from a text snippet."""
    patterns = [
        r"NT\$\s*(\d[\d,]+)",
        r"\$\s*(\d[\d,]+)",
        r"(\d[\d,]+)\s*元",
        r"(\d[\d,]+)\s*塊",
    ]
    prices = []
    for pat in patterns:
        for m in re.finditer(pat, text):
            try:
                val = int(m.group(1).replace(",", ""))
                if 10 <= val <= 100000:
                    prices.append(val)
            except ValueError:
                pass
    return min(prices) if prices else None


def _google_search_snippets(query: str, num: int = 5) -> list[str]:
    try:
        from googlesearch import search
        snippets = []
        for url in search(query, num_results=num, lang="zh-TW"):
            snippets.append(url)
        return snippets
    except Exception as exc:
        logger.warning("Google search failed: %s", exc)
        return []


def lookup_competitor_price(product_keyword: str) -> dict:
    """Search for chienchien99's historical group buy price for a product.

    Returns:
        {
            "competitor_price": int | None,
            "source_snippet": str,
            "from_cache": bool,
        }
    """
    cached = _get_cached(product_keyword)
    if cached:
        return {**cached, "from_cache": True}

    query = f"{product_keyword} {COMPETITOR_FB_PAGE}"
    snippets = _google_search_snippets(query)

    combined_text = " ".join(snippets)
    price = _extract_price(combined_text)
    snippet_text = combined_text[:500] if combined_text else ""

    _save_cache(product_keyword, price, snippet_text)

    return {
        "competitor_price": price,
        "source_snippet": snippet_text,
        "from_cache": False,
    }


def compare_prices(user_price: float, competitor_price: int | None) -> dict:
    """Compare user's group buy price against competitor.

    Returns:
        {
            "is_competitive": bool,
            "difference_amount": int,
            "recommendation": str,
        }
    """
    if competitor_price is None:
        return {
            "is_competitive": None,
            "difference_amount": None,
            "recommendation": "查無 chienchien99 歷史團購紀錄，無法比較",
        }

    diff = int(competitor_price - user_price)
    is_competitive = user_price < competitor_price

    if is_competitive:
        recommendation = f"可在文案中強調比市面團購更優惠（便宜約 {diff} 元）"
    else:
        recommendation = f"建議向廠商爭取更低的團購價格（目前比對手貴約 {abs(diff)} 元）"

    return {
        "is_competitive": is_competitive,
        "difference_amount": diff,
        "recommendation": recommendation,
    }
