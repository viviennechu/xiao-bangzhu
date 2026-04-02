"""Scrape group-buy price from a form/landing page URL."""
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

# Patterns that signal a price field (TWD amounts)
PRICE_PATTERNS = [
    re.compile(r"團購[價格][\s：:]*[NT$＄]?\s*([\d,]+)"),
    re.compile(r"優惠[價格][\s：:]*[NT$＄]?\s*([\d,]+)"),
    re.compile(r"特[惠價][\s：:]*[NT$＄]?\s*([\d,]+)"),
    re.compile(r"[NT$＄]\s*([\d,]+)"),
    re.compile(r"([\d,]{3,6})\s*元"),
]


def scrape_price(url: str) -> float | None:
    """Return the group-buy price as float, or None if not found."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text(" ", strip=True)

    for pattern in PRICE_PATTERNS:
        match = pattern.search(text)
        if match:
            raw = match.group(1).replace(",", "")
            try:
                return float(raw)
            except ValueError:
                continue

    return None
