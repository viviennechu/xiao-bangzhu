## 1. 依賴套件與基礎設定

- [x] 1.1 在 `backend/requirements.txt` 新增套件：`python-docx`、`pytrends`、`googlesearch-python`
- [x] 1.2 建立 `backend/data/` 目錄與 `.gitkeep`，用於存放 SQLite 資料庫檔案
- [x] 1.3 在 `backend/main.py` 的 startup event 中初始化 AMI 知識庫索引

## 2. AMI 知識庫（ami-knowledge）

- [x] 2.1 建立 `backend/knowledge/ami_index.py`：實作 AMI document indexing at startup，啟動時讀取所有 `.docx` 並存入 `{filename: text}` dict；以純文字索引方式常駐記憶體（ami 知識庫以純文字索引，啟動時載入記憶體）
- [x] 2.2 實作 `get_ami_snippet(topic_query: str) -> str | None`：計算關鍵字重疊評分，回傳最高分文件前 600 字；無結果時回傳 null（relevant AMI content retrieval）
- [x] 2.3 在 `backend/main.py` startup event 中呼叫 AMI index 載入，處理目錄不存在與 corrupt docx 的 exception（AMI document indexing at startup）
- [x] 2.4 實作 AMI content injection into prompts：在 blog_writer 與 reels_scriptwriter 的 prompt 組裝邏輯中，當 `ami_snippet` 不為 null 且商品分類為 educational/books 時，注入「蒙特梭利理論依據」區塊

## 3. 智慧風格選取（smart-style-selector）

- [x] 3.1 建立 `backend/ai/smart_style_selector.py`：從 `posts.json` 載入文章，依 `title + excerpt + tags` 計算關鍵字評分，回傳前 3 篇（keyword-scored article selection）；取代現有隨機抽樣邏輯（smart style selector：關鍵字評分取代隨機抽樣）
- [x] 3.2 實作 HTML stripping before style example output：用 `re.sub` 去除 HTML 標籤，保留換行
- [x] 3.3 實作 `category_filter` 可選參數：篩選含指定 category/tag 的文章；無符合時忽略 filter 退回全文搜尋（style category filtering）
- [x] 3.4 修改 `backend/ai/style_loader.py` 改為呼叫 `smart_style_selector`，移除舊有隨機抽樣邏輯

## 4. 競品比價情報（competitor-price-lookup）

- [x] 4.1 建立 `backend/search/competitor_price.py`：實作 Google search for competitor group buy price，以 `{keyword} site:facebook.com/chienchien99` 查詢，regex 抽取最低價格（競品比價：google 搜尋 + 結果解析）
- [x] 4.2 實作 SQLite caching：建立 `data/competitor_prices.db`，schema 含 `product_keyword, competitor_price, source_snippet, searched_at`；7 天 cache hit 邏輯（SQLite caching of competitor price results）
- [x] 4.3 實作 price comparison output：回傳 `is_competitive`、`difference_amount`、`recommendation` 三個欄位
- [x] 4.4 在 `backend/main.py` 新增 `GET /api/competitor-price?keyword=...` endpoint

## 5. 市場分析（market-analysis）

- [x] 5.1 建立 `backend/ai/market_analysis.py`：實作 trend analysis via Google Trends，用 `pytrends` 取得 12 個月數據，計算 3 個月均值與趨勢方向（rising/stable/declining）（market analysis：google trends pytrends + 社群搜尋）
- [x] 5.2 實作 social signal measurement via IG hashtag count：requests 抓 IG hashtag 頁面，解析貼文數，設定 `social_competition = high/low/null`
- [x] 5.3 實作 marketing mode recommendation：依 `trend_direction` + `social_competition` 組合輸出 `recommended_formats`、`primary_platform`
- [x] 5.4 實作 strategy type classification：依商品分類判斷 `montessori-knowledge` / `price-value` / `lifestyle-experience`
- [x] 5.5 所有 API 失敗時實作 graceful degradation，回傳 null 不中斷生成流程
- [x] 5.6 在 `backend/main.py` 新增 `GET /api/market-analysis?keyword=...` endpoint

## 6. Blog 長文生成（blog-writer）

- [x] 6.1 建立 `backend/ai/blog_writer.py`：實作 SEO blog post generation，系統 prompt 包含 style examples 與 AMI snippet（如有），輸出含 H1/H2 結構、大V老實說段落、hashtags（blog post structure）
- [x] 6.2 確認輸出包含 `meta_description` 欄位（120–160 字）
- [x] 6.3 實作 AMI knowledge integration in blog：當 `ami_snippet` 不為 null 且商品分類為教育類時，注入「蒙特梭利理論依據」段落
- [x] 6.4 實作 blog generation via SSE stream：`/api/generate/blog` endpoint，發送 progress + done 事件

## 7. 社群短文生成（social-writer）

- [x] 7.1 建立 `backend/ai/social_writer.py`：實作 multi-platform social post generation，單次呼叫同時產出 `ig_post`、`fb_post`、`line_post`
- [x] 7.2 確認 casual conversational tone：prompt 中明確禁止精選/嚴選/頂級/奢華等詞彙
- [x] 7.3 實作 price value mention in social post：當 `is_competitive = true` 時加入比價語句
- [x] 7.4 實作 social post generation via SSE stream：`/api/generate/social` endpoint

## 8. Reels 腳本生成（reels-scriptwriter）

- [x] 8.1 建立 `backend/ai/reels_scriptwriter.py`：實作 three-section Reels script structure，輸出包含 `hook`（問句或反常識）、`segments`（3–5 個，各含 `voiceover` + `screen_hint`）、`cta`（reels 腳本格式：固定三段結構）
- [x] 8.2 實作 non-preachy casual tone for Reels：prompt 指示在教養類商品中加入至少一句「我自己也做不到 100%」的承認
- [x] 8.3 實作 AMI knowledge in Reels script：教育類商品至少一個 segment 自然帶入 AMI 概念
- [x] 8.4 實作 reels script generation via SSE stream：`/api/generate/reels` endpoint

## 9. Copywriter 協調層重構（copywriter）

- [x] 9.1 重構 `backend/ai/copywriter.py` 為 copywriter as three-format orchestration layer：用 `asyncio.gather` 並行呼叫 blog_writer、social_writer、reels_scriptwriter；各自透過獨立 SSE stream 推送進度（三格式並行生成，各自獨立 SSE stream）
- [x] 9.2 實作 context package assembly：組合 `product`、`highlights`、`price_result`、`market_analysis`、`ami_snippet`、`style_examples` 六個欄位
- [x] 9.3 實作單一 writer 失敗時的局部回傳：失敗的 writer 欄位設為 null + error message，不中斷整體請求

## 10. 前端介面

- [x] 10.1 建立 `frontend/src/components/MarketAnalysis.jsx`：顯示趨勢方向、社群競爭度、行銷建議與競品比價結果
- [x] 10.2 建立 `frontend/src/components/MultiFormatOutput.jsx`：以分頁顯示 Blog 長文、社群短文（三平台）、Reels 腳本三種輸出
- [x] 10.3 修改 `frontend/src/App.jsx`：整合 MarketAnalysis 與 MultiFormatOutput 元件，取代原有單一文案輸出區域

## 11. 整合測試

- [x] 11.1 以教育類商品（如童書/教具）完整跑一次 pipeline，確認 AMI 注入、三格式輸出、市場分析均正常
- [x] 11.2 以一般商品（如食品/日用品）確認 AMI 不注入，社群短文禁用詞不出現
- [x] 11.3 模擬 pytrends / IG fetch 失敗，確認 graceful degradation 不中斷輸出
- [x] 11.4 測試競品比價 cache：第一次搜尋寫入 SQLite，第二次相同關鍵字從 cache 取得
