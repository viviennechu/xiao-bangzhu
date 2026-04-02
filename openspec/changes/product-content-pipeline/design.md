## Context

現有的寫文小幫手是單輸出系統：輸入商品 URL → scrape → AI 產出 LINE 群團購文。Style 範例由 `style_loader.py` 隨機抽取 3 篇 `.md` 文章，截斷至 800 字；沒有主題篩選，也沒有領域知識注入。

本次升級為「商品輸入 → 分析層 → 三格式並行輸出」的 pipeline，並引入兩個外部知識來源（AMI 手冊、競品價格）與市場分析能力。

技術棧維持不變：FastAPI + SSE（後端）、React + Vite（前端）、Claude API（AI 生成）。

## Goals / Non-Goals

**Goals:**
- 單一商品輸入可同時產出 Blog 長文、社群短文、Reels 腳本三種格式
- AMI `.docx` 手冊預先索引為純文字，供相關主題文案注入
- 依主題關鍵字從 posts.json 篩選最相關文章（取代隨機抽樣）
- Google Trends + 社群熱度提供「是否值得推廣」的初步判斷
- Google 搜尋查詢 chienchien99 歷史開團價格
- 行銷模式建議（平台 + 敘事策略）整合進分析層輸出

**Non-Goals:**
- 旅遊/生活記錄內容格式
- FB Graph API 自動爬取完整粉專
- 自動發文排程
- 向量資料庫 / embedding（本期用關鍵字匹配即可）

## Decisions

### AMI 知識庫以純文字索引，啟動時載入記憶體

**決定**：啟動時一次性讀取所有 AMI `.docx` 檔案，轉成純文字，存成 `{filename: text}` dict，常駐記憶體。生成文案時用關鍵字比對，抽取最相關片段（前 600 字）注入 prompt。

**理由**：AMI 手冊總計約 40 個 `.docx`，文字量約 30 萬字，用向量 embedding 是殺雞用牛刀，關鍵字匹配（jieba 分詞 + TF-IDF 評分）精度已足夠，且零額外 API 費用。

**替代方案**：每次生成時重新讀檔 → 延遲高，拒絕。

---

### Smart Style Selector：關鍵字評分取代隨機抽樣

**決定**：從 `posts.json` 的 `title + excerpt + tags` 欄位計算關鍵字重疊分數，選前 3 篇作為風格範例。若無相關文章（分數全為 0），退回抽取最近 5 篇中的 3 篇。

**理由**：447 篇文章跨越教養、商品、旅遊等多個主題，隨機抽樣容易拿到不相關範例。`writer.py` 已驗證關鍵字搜尋的可行性，直接移植邏輯即可。

---

### 三格式並行生成，各自獨立 SSE stream

**決定**：前端送出一個分析請求後，後端同時發起三個 AI 生成任務（asyncio.gather），各自透過獨立 SSE stream 將進度與結果推送給前端。

**理由**：三種格式的生成時間差不多（各 10–20 秒），序列執行會讓用戶等 30–60 秒，並行可壓縮至最慢那個的時間。

**替代方案**：單一 SSE stream 依序輸出 → 用戶體驗差，拒絕。

---

### Market Analysis：Google Trends pytrends + 社群搜尋

**決定**：用 `pytrends`（Google Trends 非官方 Python 套件）取得關鍵字 12 個月趨勢，用 requests 抓 IG hashtag 頁面取得貼文數量，綜合評分後輸出「建議格式」與「推廣時機」。

**評分邏輯**：
- Trends 近 3 個月均值 ≥ 50 → 適合寫長文 SEO
- Trends 近 3 個月上升趨勢 → 適合短打社群
- IG hashtag 數 > 10 萬 → 競爭激烈，需差異化角度
- IG hashtag 數 < 1 萬 → 藍海，長文 SEO 優先

**替代方案**：付費 keyword tool API（Ubersuggest/Ahrefs）→ 額外費用且過度，拒絕。

---

### 競品比價：Google 搜尋 + 結果解析

**決定**：以 `{商品關鍵字} site:facebook.com/chienchien99` 為查詢字串，用 `googlesearch-python` 抓前 5 筆結果的 snippet，用 regex 提取金額資訊。結果存入本地 SQLite 以累積歷史紀錄。

**理由**：FB 對爬蟲限制嚴，直接爬需要登入。Google 已索引大量 FB 公開貼文，snippet 通常包含價格資訊，不需登入。SQLite 讓每次查詢結果累積，越用越完整。

**替代方案**：Playwright 登入 FB 爬取 → 維護成本高、帳號封鎖風險，拒絕。

---

### Reels 腳本格式：固定三段結構

**決定**：Reels 腳本固定輸出：
1. **Hook（3 秒）**：一句話抓眼球，用問句或反常識開場
2. **內容段落（3–5 段，每段 15–30 秒）**：依商品亮點或蒙特梭利概念展開，每段有「旁白 + 畫面提示」
3. **CTA（5 秒）**：明確行動呼籲（留言/點連結/分享）

**風格基調**（來自 KOL 參考分析）：不說教、不完美、解決真實小問題，用 AMI 知識做底但說話像朋友。

## Risks / Trade-offs

- **pytrends 不穩定** → Google 偶爾封鎖請求：加 retry + exponential backoff，失敗時 graceful degradation（跳過趨勢分析，仍輸出文案）
- **AMI docx 讀取失敗（python-docx 版本問題）** → 啟動時 catch exception，知識庫為空時文案仍可生成，只是少了理論注入
- **Google 搜尋競品比價找不到結果** → 回傳「查無紀錄」，提示用戶手動補充
- **三格式並行生成 Claude API 費用** → 單次請求費用約 3 倍，但每次生成對用戶有明確價值，可接受
- **posts.json 關鍵字匹配精度有限** → 中文分詞不做 jieba（增加依賴），改用簡單字串 `in` 比對，精度略低但夠用
