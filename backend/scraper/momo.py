"""Scrape product data from momo.com.tw using BeautifulSoup."""
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9",
}


def scrape_momo(url: str) -> dict:
    """Return product dict with keys: name, description, price, images."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return {"name": "", "description": "", "price": "", "images": []}

    soup = BeautifulSoup(resp.text, "lxml")

    # ── Name: og:title is reliable on momo ──────────────────────────────
    name = ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        name = og_title["content"].strip()

    # ── Description: og:description first, then spec block ──────────────
    description = ""
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        description = og_desc["content"].strip()

    # Supplement with product spec/detail sections
    spec_parts = []
    for tag in soup.find_all(["li", "p", "div"], class_=re.compile(r"prdDtl|goods_spec|spec|detail|feature", re.I)):
        text = tag.get_text(" ", strip=True)
        if 10 < len(text) < 300:
            spec_parts.append(text)
    if spec_parts:
        description = description + " " + " ".join(spec_parts[:6])
    description = description.strip()[:2000]

    # ── Price: try og:price, then structured data, then regex ───────────
    price = ""
    og_price = soup.find("meta", property="product:price:amount")
    if og_price and og_price.get("content"):
        price = og_price["content"].replace(",", "")

    if not price:
        # Look for JSON-LD price
        for script in soup.find_all("script", type="application/ld+json"):
            text = script.get_text()
            match = re.search(r'"price"\s*:\s*"?([\d,]+)"?', text)
            if match:
                price = match.group(1).replace(",", "")
                break

    if not price:
        # Last resort: find visible price elements
        for tag in soup.find_all(class_=re.compile(r"current.?price|salePrice|finalPrice", re.I)):
            text = tag.get_text(strip=True)
            match = re.search(r"[\d,]{2,}", text)
            if match:
                price = match.group().replace(",", "")
                break

    # ── Images: og:image + product images ───────────────────────────────
    images = []
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        images.append(og_image["content"])

    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        if (src and src.startswith("http") and src not in images
                and any(kw in src.lower() for kw in ["goods", "product", "img"])):
            images.append(src)
        if len(images) >= 5:
            break

    return {
        "name": name,
        "description": description,
        "price": str(price),
        "images": images,
    }
