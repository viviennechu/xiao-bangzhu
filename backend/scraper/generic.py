"""Scrape product data from a generic brand official website using BeautifulSoup."""
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}


def scrape_generic(url: str) -> dict:
    """Return product dict with keys: name, description, price, images."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return {"name": "", "description": "", "price": "", "images": []}

    soup = BeautifulSoup(resp.text, "lxml")

    # Remove nav/footer noise
    for tag in soup.find_all(["nav", "footer", "header", "script", "style"]):
        tag.decompose()

    # Product name: try <h1> first, then <title>
    name = ""
    h1 = soup.find("h1")
    if h1:
        name = h1.get_text(strip=True)
    if not name:
        title = soup.find("title")
        if title:
            name = title.get_text(strip=True).split("|")[0].split("-")[0].strip()

    # Description: meta description first, then main content blocks
    description = ""
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        description = meta_desc["content"]

    if len(description) < 100:
        parts = []
        for tag in soup.find_all(["p", "li", "div"], limit=50):
            text = tag.get_text(" ", strip=True)
            if 20 < len(text) < 500:
                parts.append(text)
        if parts:
            description = " ".join(parts[:8])

    # Price
    price = ""
    price_tag = soup.find(class_=re.compile(r"price|Price|售價|定價"))
    if price_tag:
        text = price_tag.get_text(strip=True)
        match = re.search(r"[\d,]+", text)
        if match:
            price = match.group().replace(",", "")

    # Images: og:image first, then page images
    images = []
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        images.append(og_image["content"])

    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        if src and src.startswith("http") and src not in images:
            images.append(src)
        if len(images) >= 5:
            break

    return {
        "name": name,
        "description": description[:2000],
        "price": str(price),
        "images": images,
    }
