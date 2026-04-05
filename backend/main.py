import asyncio
import json
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

load_dotenv()

from scraper.momo import scrape_momo
from scraper.generic import scrape_generic
from scraper.price import scrape_price
from ai.highlight import extract_highlights
from ai.shooting import generate_shooting_plan
from ai.copywriter import generate_copy, generate_all
from search.social import search_social_references, SearchUnavailableError
from knowledge.ami_index import load_index as load_ami_index
from search.competitor_price import lookup_competitor_price, compare_prices
from ai.market_analysis import analyze_market
from ai.translator import translate


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(load_ami_index)
    yield


app = FastAPI(title="寫文小幫手 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── SSE scrape endpoint ────────────────────────────────────────────────────────

async def scrape_stream(url: str):
    """Stream scraping progress and final product data via SSE."""
    async def event_gen():
        yield {"event": "progress", "data": json.dumps({"message": "正在抓取商品資料..."})}

        # Determine scraper by domain
        if "momo.com.tw" in url:
            product = await asyncio.to_thread(scrape_momo, url)
        elif "books.com.tw" in url:
            # books.com.tw blocks all scrapers — skip directly to manual input
            yield {"event": "error", "data": json.dumps({"message": "博客來有防爬蟲保護，請手動複製商品名稱和介紹貼到②商品亮點欄位"})}
            return
        else:
            product = await asyncio.to_thread(scrape_generic, url)

        if not product.get("name"):
            yield {"event": "progress", "data": json.dumps({"message": "BeautifulSoup 無結果，切換 Playwright..."})}
            from scraper.playwright_scraper import scrape_with_playwright
            product = await scrape_with_playwright(url)

        if not product.get("name"):
            yield {"event": "error", "data": json.dumps({"message": "無法取得商品資料，請手動輸入"})}
            return

        yield {"event": "progress", "data": json.dumps({"message": "正在分析頁面內容..."})}
        yield {"event": "done", "data": json.dumps(product)}

    return EventSourceResponse(event_gen())


@app.get("/api/scrape")
async def scrape_endpoint(url: str = Query(...)):
    return await scrape_stream(url)


# ── Highlights ─────────────────────────────────────────────────────────────────

class ProductData(BaseModel):
    name: str
    description: str = ""
    price: str = ""
    images: list[str] = []


@app.post("/api/highlights")
async def highlights_endpoint(product: ProductData):
    highlights = await extract_highlights(product.model_dump())
    return {"highlights": highlights}


# ── Shooting plan ──────────────────────────────────────────────────────────────

class HighlightsPayload(BaseModel):
    highlights: list[dict]


@app.post("/api/shooting-plan")
async def shooting_plan_endpoint(payload: HighlightsPayload):
    plan = await generate_shooting_plan(payload.highlights)
    return plan


# ── Social references ──────────────────────────────────────────────────────────

class SocialSearchPayload(BaseModel):
    product_name: str


@app.post("/api/social-references")
async def social_references_endpoint(payload: SocialSearchPayload):
    try:
        results = await asyncio.to_thread(search_social_references, payload.product_name)
        return {"references": results}
    except SearchUnavailableError:
        return {"error": "素材搜尋暫時無法使用", "references": []}


# ── Price compare ──────────────────────────────────────────────────────────────

class PricePayload(BaseModel):
    retail_price: float
    group_buy_price: float | None = None
    group_buy_url: str | None = None


@app.post("/api/price-compare")
async def price_compare_endpoint(payload: PricePayload):
    group_buy = payload.group_buy_price

    if group_buy is None and payload.group_buy_url:
        group_buy = await asyncio.to_thread(scrape_price, payload.group_buy_url)
        if group_buy is None:
            raise HTTPException(status_code=422, detail="無法取得團購價格，請手動輸入")

    if group_buy is None:
        raise HTTPException(status_code=422, detail="請提供團購價格")

    retail = payload.retail_price
    is_warning = group_buy >= retail
    savings_amount = round(retail - group_buy, 0) if not is_warning else 0
    savings_percent = round((retail - group_buy) / retail * 100, 1) if not is_warning else 0

    return {
        "is_warning": is_warning,
        "retail_price": retail,
        "group_buy_price": group_buy,
        "savings_amount": savings_amount,
        "savings_percent": savings_percent,
    }


# ── Competitor price ───────────────────────────────────────────────────────────

class CompetitorPricePayload(BaseModel):
    keyword: str
    group_buy_price: float | None = None


@app.post("/api/competitor-price")
async def competitor_price_endpoint(payload: CompetitorPricePayload):
    result = await asyncio.to_thread(lookup_competitor_price, payload.keyword)
    comparison = None
    if payload.group_buy_price is not None:
        comparison = compare_prices(payload.group_buy_price, result.get("competitor_price"))
    return {**result, "comparison": comparison}


@app.get("/api/competitor-price")
async def competitor_price_get_endpoint(keyword: str = Query(...), group_buy_price: float | None = None):
    result = await asyncio.to_thread(lookup_competitor_price, keyword)
    comparison = None
    if group_buy_price is not None:
        comparison = compare_prices(group_buy_price, result.get("competitor_price"))
    return {**result, "comparison": comparison}


# ── Market analysis ────────────────────────────────────────────────────────────

@app.get("/api/market-analysis")
async def market_analysis_endpoint(
    keyword: str = Query(...),
    product_category: str = Query(default="general"),
):
    result = await asyncio.to_thread(analyze_market, keyword, product_category)
    return result


# ── Copywrite (legacy LINE-only) ───────────────────────────────────────────────

class CopywritePayload(BaseModel):
    product: dict
    highlights: list[dict]
    price_result: dict | None = None


@app.post("/api/copywrite")
async def copywrite_endpoint(payload: CopywritePayload):
    copy = await generate_copy(
        product=payload.product,
        highlights=payload.highlights,
        price_result=payload.price_result,
    )
    return {"copy": copy}


# ── Three-format generation (SSE streams) ──────────────────────────────────────

class GeneratePayload(BaseModel):
    product: dict
    highlights: list[dict]
    price_result: dict | None = None
    market_analysis: dict | None = None
    competitor_comparison: dict | None = None


@app.post("/api/generate/blog")
async def generate_blog_endpoint(payload: GeneratePayload):
    async def event_gen():
        yield {"event": "progress", "data": json.dumps({"message": "正在生成 Blog 長文..."})}
        result = await generate_all(
            product=payload.product,
            highlights=payload.highlights,
            price_result=payload.price_result,
            market_analysis=payload.market_analysis,
            competitor_comparison=payload.competitor_comparison,
        )
        if result.get("errors", {}).get("blog"):
            yield {"event": "error", "data": json.dumps({"message": result["errors"]["blog"]})}
        else:
            yield {"event": "done", "data": json.dumps(result.get("blog") or {})}
    return EventSourceResponse(event_gen())


@app.post("/api/generate/social")
async def generate_social_endpoint(payload: GeneratePayload):
    async def event_gen():
        yield {"event": "progress", "data": json.dumps({"message": "正在生成社群短文..."})}
        result = await generate_all(
            product=payload.product,
            highlights=payload.highlights,
            price_result=payload.price_result,
            market_analysis=payload.market_analysis,
            competitor_comparison=payload.competitor_comparison,
        )
        if result.get("errors", {}).get("social"):
            yield {"event": "error", "data": json.dumps({"message": result["errors"]["social"]})}
        else:
            yield {"event": "done", "data": json.dumps(result.get("social") or {})}
    return EventSourceResponse(event_gen())


@app.post("/api/generate/reels")
async def generate_reels_endpoint(payload: GeneratePayload):
    async def event_gen():
        yield {"event": "progress", "data": json.dumps({"message": "正在生成 Reels 腳本..."})}
        result = await generate_all(
            product=payload.product,
            highlights=payload.highlights,
            price_result=payload.price_result,
            market_analysis=payload.market_analysis,
            competitor_comparison=payload.competitor_comparison,
        )
        if result.get("errors", {}).get("reels"):
            yield {"event": "error", "data": json.dumps({"message": result["errors"]["reels"]})}
        else:
            yield {"event": "done", "data": json.dumps(result.get("reels") or {})}
    return EventSourceResponse(event_gen())


@app.post("/api/generate/all")
async def generate_all_endpoint(payload: GeneratePayload):
    """Generate all three formats at once (non-streaming)."""
    result = await generate_all(
        product=payload.product,
        highlights=payload.highlights,
        price_result=payload.price_result,
        market_analysis=payload.market_analysis,
        competitor_comparison=payload.competitor_comparison,
    )
    return result


# ── 大V翻譯機 ──────────────────────────────────────────────────────────────────

class TranslatePayload(BaseModel):
    draft: str
    persona: str        # "bigv" | "wa"
    output_format: str  # "blog" | "ig_stories" | "group_fire"


@app.post("/api/translate")
async def translate_endpoint(payload: TranslatePayload):
    if payload.persona not in ("bigv", "wa", "sammy", "zhenzen"):
        raise HTTPException(status_code=422, detail="persona 必須是 bigv | wa | sammy | zhenzen")
    if payload.output_format not in ("blog", "ig_stories", "group_fire"):
        raise HTTPException(status_code=422, detail="output_format 必須是 blog | ig_stories | group_fire")
    result = await translate(
        draft=payload.draft,
        persona=payload.persona,
        output_format=payload.output_format,
    )
    return result
