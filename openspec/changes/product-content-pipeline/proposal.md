## Why

現有的寫文小幫手只能產出 LINE 群團購文，缺乏 SEO 部落格長文、社群短文素材與 Reels 腳本，也無法整合蒙特梭利知識庫或分析市場趨勢，導致每次寫文需要大量人工補充，無法發揮 KOL 的專業優勢。

## What Changes

- **新增：三格式輸出**——單一商品輸入可同時產出 Blog 長文（SEO）、社群短文（IG/FB/LINE）、Reels 腳本
- **新增：行銷模式建議**——根據商品特性與市場趨勢，建議最適合的推廣平台與敘事策略
- **新增：SEO/趨勢預判**——整合 Google Trends 與社群熱度分析，預判是否值得推廣、適合哪種格式
- **新增：AMI 蒙特梭利知識庫整合**——自動從 AMI 課程文件中抽取相關理論，注入教養/早教/書本類文案
- **新增：競品比價情報**——透過 Google 搜尋查詢 chienchien99 歷史團購價格，輔助廠商議價
- **新增：智慧風格選取**——依文章主題從 447 篇文章中篩選最相關範例，取代現有隨機抽樣
- **修改：Copywriter**——現有 LINE 文案生成升級為三格式並行輸出

## Non-Goals

- 旅遊/生活記錄相關內容（另開專案）
- 自動爬取 FB 粉專完整貼文庫（技術限制，僅做搜尋式查詢）
- FB Graph API 整合（需另行申請權限）
- 自動發文排程

## Capabilities

### New Capabilities

- `market-analysis`: SEO 趨勢預判 + 行銷模式建議，輸出「是否值得推廣」與「建議平台/策略」
- `ami-knowledge`: AMI 蒙特梭利知識庫，從 `.docx` 手冊中抽取並索引理論內容，供文案注入
- `smart-style-selector`: 依主題關鍵字從 posts.json 篩選最相關文章範例，取代隨機抽樣
- `blog-writer`: SEO 導向部落格長文生成（1500–2500 字，含標題、H2 結構、關鍵字）
- `social-writer`: 社群短文素材生成（IG/FB/LINE，150–300 字）
- `reels-scriptwriter`: Reels 腳本生成（Hook 3 秒 + 3–5 個段落 + CTA，含配音文字稿）
- `competitor-price-lookup`: 透過 Google 搜尋查詢 chienchien99 歷史開團價格

### Modified Capabilities

- `copywriter`: 現有 LINE 文案生成重構為三格式並行輸出的協調層

## Impact

- 新增後端模組：`backend/ai/blog_writer.py`、`backend/ai/social_writer.py`、`backend/ai/reels_scriptwriter.py`
- 新增後端模組：`backend/ai/market_analysis.py`、`backend/search/competitor_price.py`
- 新增後端模組：`backend/knowledge/ami_index.py`、`backend/ai/smart_style_selector.py`
- 修改：`backend/ai/copywriter.py`（改為三格式協調層）
- 修改：`backend/ai/style_loader.py`（接入 smart-style-selector）
- 修改：`backend/main.py`（新增 API endpoints）
- 新增前端元件：`frontend/src/components/MarketAnalysis.jsx`、`frontend/src/components/MultiFormatOutput.jsx`
- 新增依賴：`python-docx`（讀取 AMI .docx）、`googlesearch-python` 或 `requests`（競品查詢）
