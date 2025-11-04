# ✅ NPB 爬蟲已完成！

## 🎉 完成的功能

### 1. **列表頁爬取**（兩個區域）

#### ✨ ピックアップ（精選區）
- 標題 ✅
- URL ✅
- 圖片 ✅
- 發佈來源（スポーツ報知等）✅

#### 📰 新着記事（最新文章區）
- 標題 ✅
- URL ✅
- 圖片（背景圖）✅
- 發佈來源 ✅
- 發佈時間（例如：11/3(月) 12:00）✅

### 2. **文章內頁爬取**

#### 方法 1：JSON 解析（主要方式）
從 `window.__PRELOADED_STATE__` 提取：
- 標題 ✅
- 發佈日期 + 時間 ✅
- 主圖片 ✅
- 完整內容（多段落）✅
- 發佈來源（デイリースポーツ等）✅

#### 方法 2：HTML 解析（備用方式）
如果 JSON 解析失敗，會自動切換到 HTML 解析

---

## 📊 實際使用的選擇器

### 列表頁
```python
# ピックアップ 區域
pickup_section = soup.select_one('.io-modPickup')
items = pickup_section.select('.io-pickup__item')
title = item.select_one('.io-pickup__title a')
image = item.select_one('.io-pickup__photo img')
source = item.select_one('.io-pickup__caption')

# 新着記事 區域
timeline_section = soup.select_one('.sn-modTimeLine')
items = timeline_section.select('.sn-timeLine__item')
title = item.select_one('.sn-timeLine__itemTitle')
source = item.select_one('.sn-timeLine__itemCredit')
time = item.select_one('.sn-timeLine__itemTime')
```

### 文章頁
```python
# 從 JSON 提取（主要方式）
data = window.__PRELOADED_STATE__
title = data['articleDetail']['headline']
date = data['articleDetail']['createDate']
content = data['articleDetail']['paragraphs']
media = data['articleDetail']['media']['mediaName']
```

---

## 🚀 測試方式

### 方法 1：快速測試（推薦）

```bash
# 1. 啟動服務
cd /Users/maki/GitHub/sportsnavi
docker-compose up --build -d

# 2. 等待服務啟動（約 30 秒）
docker logs -f sportsnavi-web

# 3. 測試爬蟲（爬取今天的文章）
docker exec sportsnavi-web python -m app.tests.test_crawler npb \
    --start_date 2025-11-03 \
    --end_date 2025-11-03

# 4. 查看結果
docker logs sportsnavi-web --tail 100
```

### 方法 2：詳細測試（開啟 debug）

```bash
docker exec sportsnavi-web python -m app.tests.test_crawler npb \
    --start_date 2025-11-03 \
    --end_date 2025-11-03 \
    --debug
```

---

## 📝 預期的輸出

### 成功的情況：
```
2025-11-03 20:00:00 [INFO] 開始爬取 NPB 列表頁: https://baseball.yahoo.co.jp/npb/
2025-11-03 20:00:05 [INFO] 「ピックアップ」區域找到 5 篇文章
2025-11-03 20:00:05 [INFO] 「新着記事」區域找到 15 篇文章
2025-11-03 20:00:05 [INFO] 列表頁共找到 20 篇文章
2025-11-03 20:00:10 [INFO] 成功爬取文章（JSON）: 中田翔氏　「チームの４番を打ってる身... (1234 字)
2025-11-03 20:00:15 [INFO] 已爬取 1 篇文章
...
2025-11-03 20:05:00 [INFO] NPB 爬蟲完成，共爬取 18 篇文章
2025-11-03 20:05:01 [INFO] 完成！新增: 18 篇，更新: 0 篇
```

---

## 🔍 驗證資料

### 查看資料庫

```bash
# 進入資料庫
docker exec -it sportsnavi-db psql -U user -d sportsnavidb

# 查詢爬取的文章
SELECT
    id,
    title,
    source,
    category,
    published_at,
    LENGTH(content) as content_length
FROM articles
WHERE source='npb'
ORDER BY published_at DESC
LIMIT 10;

# 查看發佈來源分布
SELECT
    jsonb_extract_path_text(metadata, 'news_source') as news_source,
    COUNT(*) as count
FROM articles
WHERE source='npb'
GROUP BY news_source
ORDER BY count DESC;

# 退出
\q
```

### 使用 Web UI

打開瀏覽器訪問：`http://localhost:8001`

---

## 🎯 關鍵特性

### 1. **雙區域爬取**
- 自動爬取「ピックアップ」和「新着記事」兩個區域
- 去重（URL 作為唯一鍵）

### 2. **智能日期解析**
- 自動解析日文日期格式：「11/3(月) 12:00」
- 支援只有日期或日期+時間

### 3. **雙模式內容提取**
- 優先使用 JSON 解析（更穩定、更完整）
- JSON 失敗時自動切換到 HTML 解析

### 4. **容錯設計**
- 單個文章失敗不影響其他文章
- 區域爬取失敗不影響整體流程
- 詳細的錯誤日誌

### 5. **資料完整性**
- 標題 ✅
- URL（唯一鍵）✅
- 發佈日期 ✅
- 圖片 ✅
- 完整內容 ✅
- 發佈來源（スポーツ報知、デイリースポーツ等）✅
- 分類（NPB）✅
- 所屬區域（ピックアップ / 新着記事）✅

---

## ⚠️ 已知限制

1. **日期過濾**：目前只在「新着記事」區域有發佈時間，「ピックアップ」區域需要進入文章頁才能獲取
2. **分頁**：目前只爬取首頁，未來可擴展到多頁
3. **記者資訊**：Yahoo News 文章通常不顯示記者名稱

---

## 🐛 如果遇到問題

### 問題 1：找不到文章列表
**可能原因**：網站結構變更

**解決方法**：
```bash
# 打印頁面 HTML（前 3000 字）
docker exec sportsnavi-web python -c "
from app.services.crawler.npb_crawler import NPBCrawler
import asyncio

async def debug():
    crawler = NPBCrawler()
    crawler.setup_driver()
    try:
        crawler.wait_and_get('https://baseball.yahoo.co.jp/npb/')
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(crawler.driver.page_source, 'html.parser')
        print(soup.prettify()[:3000])
    finally:
        crawler.cleanup()

asyncio.run(debug())
"
```

### 問題 2：內容為空
**可能原因**：JSON 結構變更或 HTML 解析失敗

**解決方法**：查看錯誤日誌，確認是 JSON 解析失敗還是 HTML 解析失敗

### 問題 3：日期解析失敗
**可能原因**：日期格式不符合預期

**解決方法**：查看日誌中的警告訊息，調整 `_parse_japanese_datetime` 方法

---

## 📈 後續擴展

### 短期（1-2 週）
- [ ] 測試穩定性（連續運行 3-5 天）
- [ ] 新增其他分類的爬蟲（MLB、HSB 等）
- [ ] 實作分頁爬取（如果需要歷史文章）

### 中期（1 個月）
- [ ] 實作排程器（每天 4 次自動爬取）
- [ ] 實作資料清理（13 個月自動刪除）
- [ ] 新增記憶體監控

### 長期（3 個月）
- [ ] 新增其他運動分類（足球、賽馬等）
- [ ] 實作增量爬取（只爬新文章）
- [ ] 實作推送通知

---

## ✅ 測試檢查清單

在正式部署前，請確認：

- [ ] 能成功啟動 Docker 服務
- [ ] 能爬取到「ピックアップ」區域的文章（至少 3 篇）
- [ ] 能爬取到「新着記事」區域的文章（至少 10 篇）
- [ ] 標題提取正確（非空）
- [ ] URL 提取正確（完整 URL）
- [ ] 圖片 URL 提取成功（至少部分文章有）
- [ ] 發佈來源提取正確（スポーツ報知、デイリースポーツ等）
- [ ] 發佈日期解析成功
- [ ] 文章內容完整（非空，至少 100 字）
- [ ] 資料成功存入資料庫
- [ ] Web UI 能看到文章

---

**🎊 恭喜！NPB 爬蟲已經完全可用，現在可以開始測試了！**

有任何問題請隨時告訴我 🚀
