"""多平台商品比價 — 查詢 Shopee、PChome、Momo 等平台的最低售價。"""
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9",
}


def _search_shopee(keyword: str) -> dict | None:
    """Shopee 公開搜尋 API。"""
    try:
        url = "https://shopee.tw/api/v4/search/search_items/"
        params = {
            "by": "relevancy",
            "keyword": keyword,
            "limit": 5,
            "newest": 0,
            "order": "desc",
            "page_type": "search",
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        items = data.get("items") or []
        prices = []
        for item in items:
            item_data = item.get("item_basic") or item
            price_raw = item_data.get("price") or item_data.get("price_min")
            if price_raw:
                prices.append(price_raw / 100000)  # Shopee 單位是 1/100000 元
        if not prices:
            return None
        min_price = min(prices)
        return {"platform": "蝦皮", "price": round(min_price), "url": f"https://shopee.tw/search?keyword={keyword}"}
    except Exception as e:
        logger.warning("Shopee search failed: %s", e)
        return None


def _search_pchome(keyword: str) -> dict | None:
    """PChome 24h 搜尋 — 從 HTML JSON-LD 抓價格。"""
    try:
        url = f"https://24h.pchome.com.tw/search/#/q={requests.utils.quote(keyword)}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        prices = re.findall(r'"price"\s*:\s*"(\d+)"', resp.text)
        if not prices:
            return None
        min_price = min(int(p) for p in prices[:20] if int(p) > 10)
        return {"platform": "PChome 24h", "price": min_price, "url": f"https://24h.pchome.com.tw/search/#/q={keyword}"}
    except Exception as e:
        logger.warning("PChome search failed: %s", e)
        return None


def _search_momo(keyword: str) -> dict | None:
    """Momo 搜尋頁爬價格 — 從 JSON-LD 抓。"""
    try:
        url = "https://www.momoshop.com.tw/search/searchShop.jsp"
        params = {"keyword": keyword, "searchType": 1, "curPage": 1}
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        # JSON-LD schema: "price": "1399"
        prices = re.findall(r'"price"\s*:\s*"(\d+)"', resp.text)
        if not prices:
            prices = re.findall(r'"finalPrice"\s*:\s*(\d+(?:\.\d+)?)', resp.text)
        if not prices:
            return None
        min_price = min(int(p) for p in prices[:20] if int(p) > 10)
        return {"platform": "momo", "price": min_price, "url": f"https://www.momoshop.com.tw/search/searchShop.jsp?keyword={keyword}"}
    except Exception as e:
        logger.warning("Momo search failed: %s", e)
        return None


def _search_yahoo(keyword: str) -> dict | None:
    """Yahoo 購物搜尋。"""
    try:
        url = "https://tw.buy.yahoo.com/search/product"
        params = {"p": keyword}
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        prices = re.findall(r'"price"\s*:\s*(\d+)', resp.text)
        if not prices:
            prices = re.findall(r'NT\$\s*([0-9,]+)', resp.text)
            prices = [p.replace(",", "") for p in prices]
        if not prices:
            return None
        min_price = min(int(p) for p in prices[:10] if int(p) > 10)
        return {"platform": "Yahoo 購物", "price": min_price, "url": f"https://tw.buy.yahoo.com/search/product?p={keyword}"}
    except Exception as e:
        logger.warning("Yahoo search failed: %s", e)
        return None


def search_platform_prices(keyword: str) -> list[dict]:
    """並行查詢各平台最低價，回傳有結果的平台清單，依價格排序。"""
    searchers = [_search_shopee, _search_pchome, _search_momo, _search_yahoo]
    results = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fn, keyword): fn.__name__ for fn in searchers}
        for future in as_completed(futures, timeout=15):
            try:
                result = future.result()
                if result and result.get("price"):
                    results.append(result)
            except Exception:
                pass

    results.sort(key=lambda x: x["price"])
    return results
