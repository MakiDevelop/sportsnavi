# 🎯 接下來要做什麼？

## ✅ 已完成的工作

1. ✅ **清理舊爬蟲** - 刪除 10 個房地產爬蟲
2. ✅ **更新配置** - config.py、.env、docker-compose.yml
3. ✅ **創建 NPB 爬蟲** - 包含完整的範本和 TODO 註解
4. ✅ **更新測試文件** - test_crawler.py

## 🚧 NPB 爬蟲需要你完成的部分

我創建的 NPB 爬蟲是一個**模板**，包含了架構和邏輯，但需要你根據實際的 Yahoo Sports 網站結構填充細節。

### 📍 需要調整的地方（有 TODO 標記）

在 `app/services/crawler/npb_crawler.py` 中：

#### 1. **列表頁 URL** (第 37-42 行)
```python
# TODO: 根據實際網站結構調整 URL
list_url = f"{self.base_url}news/"
```

**你需要做：**
1. 在瀏覽器打開 `https://baseball.yahoo.co.jp/npb/`
2. 找到新聞列表頁面
3. 確認 URL 格式（例如：`/npb/news/`、`/npb/articles/` 等）
4. 更新程式碼

---

#### 2. **列表頁選擇器** (第 53-64 行)
```python
# TODO: 根據實際網站結構調整選擇器
articles_html = soup.select('.bb-newsList__item')  # ← 這裡需要調整
```

**你需要做：**
1. 在列表頁按 F12 打開開發者工具
2. 檢查文章列表的 HTML 結構
3. 找到包含文章項目的 CSS 類名或標籤
4. 更新選擇器

**常見的選擇器範例：**
- `.news-list .news-item`
- `article.article-card`
- `.bb-newsList__item`
- `div[class*="news"]`

---

#### 3. **提取標題、URL、圖片** (第 72-85 行)
```python
# TODO: 根據實際 HTML 結構調整以下選擇器
title_elem = item.select_one('.bb-newsList__title')  # 範例
url = link_elem.get('href') if link_elem else None
img_elem = item.select_one('img')
```

**你需要做：**
1. 在每個文章項目中找到：
   - 標題元素（通常是 `<h2>`、`<h3>` 或有特定 class 的 `<a>`）
   - URL 連結（通常是 `<a href="...">`）
   - 圖片（通常是 `<img src="...">`）
2. 更新選擇器

---

#### 4. **文章內容頁選擇器** (第 157-180 行)
```python
# TODO: 根據實際網站結構調整選擇器
content_elem = soup.select_one('.bb-articleText')  # ← 根據實際網站調整
```

**你需要做：**
1. 點擊進入一篇文章
2. 在文章頁按 F12
3. 找到包含文章內容的元素
4. 更新選擇器

**常見的內容選擇器：**
- `.article-body`
- `.article-content`
- `.bb-articleText`
- `article .content`

---

## 🛠️ 調試步驟

### 方法 1：直接運行爬蟲（推薦先用這個）

```bash
# 1. 啟動 Docker
docker-compose up -d

# 2. 運行爬蟲（會自動啟動 Chrome 並開始爬取）
docker exec sportsnavi-web python -m app.tests.test_crawler npb \
    --start_date 2025-11-01 \
    --end_date 2025-11-03

# 3. 查看日誌
docker logs -f sportsnavi-web
```

---

### 方法 2：創建調試腳本（建議在調整選擇器時使用）

創建 `debug_npb.py`：

```python
from app.services.crawler.npb_crawler import NPBCrawler
import asyncio

async def debug():
    crawler = NPBCrawler()
    crawler.setup_driver()

    try:
        # 測試列表頁
        print("=== 測試列表頁 ===")
        url = "https://baseball.yahoo.co.jp/npb/news/"
        crawler.wait_and_get(url)

        # 打印頁面 HTML（前 2000 字）
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(crawler.driver.page_source, 'html.parser')
        print(soup.prettify()[:2000])

        # 嘗試提取文章列表
        articles = soup.select('.bb-newsList__item')  # ← 調整這裡
        print(f"\n找到 {len(articles)} 篇文章")

        if articles:
            # 打印第一篇文章的 HTML
            print("\n=== 第一篇文章 ===")
            print(articles[0].prettify())

    finally:
        crawler.cleanup()

if __name__ == '__main__':
    asyncio.run(debug())
```

運行：
```bash
docker exec sportsnavi-web python debug_npb.py
```

---

### 方法 3：使用瀏覽器開發者工具

1. **打開網站**：`https://baseball.yahoo.co.jp/npb/`
2. **按 F12** 打開開發者工具
3. **點擊選擇器圖標**（Element Selector）
4. **點擊頁面上的文章標題**
5. **查看 HTML 結構**

範例：
```html
<div class="bb-newsList__item">
    <a href="/npb/news/123">
        <h3 class="bb-newsList__title">文章標題</h3>
        <img src="image.jpg" class="bb-newsList__image">
        <time class="bb-newsList__date">2025-11-03</time>
    </a>
</div>
```

根據這個結構，你需要更新：
```python
articles_html = soup.select('.bb-newsList__item')
title_elem = item.select_one('.bb-newsList__title')
date_elem = item.select_one('.bb-newsList__date')
```

---

## 📋 完整測試流程

### 步驟 1：啟動服務
```bash
cd /Users/maki/GitHub/sportsnavi
docker-compose up --build -d
```

### 步驟 2：檢查服務狀態
```bash
docker ps
# 應該看到 sportsnavi-web 和 sportsnavi-db 都在運行
```

### 步驟 3：測試爬蟲
```bash
# 先測試 1-2 天的資料
docker exec sportsnavi-web python -m app.tests.test_crawler npb \
    --start_date 2025-11-01 \
    --end_date 2025-11-02 \
    --debug  # 開啟 debug 模式查看更多日誌
```

### 步驟 4：查看結果

#### 方法 A：查看日誌
```bash
docker logs sportsnavi-web --tail 100
```

#### 方法 B：查看資料庫
```bash
# 進入資料庫容器
docker exec -it sportsnavi-db psql -U user -d sportsnavidb

# 查詢資料
SELECT id, title, source, published_at
FROM articles
WHERE source='npb'
ORDER BY published_at DESC
LIMIT 10;

# 退出
\q
```

#### 方法 C：使用 Web UI
```bash
# 訪問
http://localhost:8000
```

---

## ⚠️ 常見問題

### 問題 1：爬蟲找不到文章
**症狀**：日誌顯示「第 1 頁未找到文章列表」

**解決方法**：
1. 列表頁選擇器不正確
2. 使用 `debug_npb.py` 打印 HTML
3. 在瀏覽器開發者工具中確認選擇器

---

### 問題 2：文章內容為空
**症狀**：日誌顯示「文章內容為空」

**解決方法**：
1. 內容選擇器不正確
2. 進入實際文章頁面檢查 HTML 結構
3. 更新 `content_elem` 的選擇器

---

### 問題 3：日期解析失敗
**症狀**：日誌顯示「無法解析日期」

**解決方法**：
1. 檢查日期元素的實際格式
2. 如果是日文日期（例如：「2025年11月3日」）
3. 在 `base.py` 的 `parse_flexible_date` 中新增對應格式：

```python
# 新增日文日期格式
'%Y年%m月%d日',          # 2025年11月3日
'%Y年%m月%d日 %H:%M',    # 2025年11月3日 12:00
```

---

### 問題 4：Docker 記憶體不足
**症狀**：Chrome 無法啟動或崩潰

**解決方法**：
```bash
# 檢查 Docker 記憶體設定
docker stats

# 如果不夠，調整 docker-compose.yml
# 降低 web 服務的記憶體限制：
deploy:
  resources:
    limits:
      memory: 4G  # 從 6G 降到 4G
```

---

## ✅ 完成檢查清單

在測試通過後，確認：

- [ ] 列表頁能正確載入
- [ ] 能找到文章列表（至少 1 篇）
- [ ] 標題提取正確
- [ ] URL 提取正確且完整
- [ ] 能進入文章頁面
- [ ] 內容提取完整（不為空）
- [ ] 日期解析成功
- [ ] 資料成功存入資料庫
- [ ] Web UI 能看到文章

---

## 🎉 測試成功後

恭喜！你已經完成核心功能。接下來可以：

### 選項 A：繼續實作其他爬蟲
```bash
# 複製 npb_crawler.py
cp app/services/crawler/npb_crawler.py app/services/crawler/mlb_crawler.py

# 修改類名和 URL
class MLBCrawler(BaseCrawler):
    def __init__(self):
        self.source_name = "MLB"
        self.base_url = "https://baseball.yahoo.co.jp/mlb/"
```

### 選項 B：實作進階功能
- 資料保留策略（13 個月自動清理）
- 排程器（每天 4 次自動爬取）
- 記憶體監控

### 選項 C：優化現有爬蟲
- 新增錯誤處理
- 提升爬取速度
- 新增更多日期格式支援

---

## 📞 需要協助？

如果遇到問題，請提供：
1. 完整的錯誤訊息
2. 爬蟲日誌（`docker logs sportsnavi-web`）
3. 目標網站的 HTML 結構（開發者工具截圖）

我可以幫你調整選擇器或解決具體問題！

---

**現在，請先執行步驟 1-3，看看能否成功運行爬蟲。有任何問題隨時告訴我！** 🚀
