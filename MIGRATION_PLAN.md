# 🔄 專案遷移計劃：從 REAS 到 Sportsnavi

## 📊 當前狀況分析

### ✅ 已複製的架構（保留）

```
sportsnavi/
├── app/
│   ├── core/               ✅ 核心配置（需修改）
│   │   ├── config.py       → 更新為 Yahoo Sports 配置
│   │   ├── database.py     ✅ 保留不變
│   │   ├── db_utils.py     ✅ 保留不變
│   │   └── logging_config.py ✅ 保留不變
│   ├── models/             ✅ 資料模型（可能需微調）
│   │   └── article.py      → 檢查欄位是否適用
│   ├── schemas/            ✅ Pydantic schemas
│   │   └── article.py      ✅ 保留不變
│   ├── api/                ✅ REST API
│   │   └── v1/             ✅ 保留不變
│   ├── services/
│   │   └── crawler/
│   │       └── base.py     ✅ 保留（可能需微調）
│   ├── templates/          ✅ Web UI
│   ├── static/             ✅ 靜態資源
│   └── tests/              → 需更新測試
├── docker-compose.yml      ✅ 保留（需微調）
├── Dockerfile              ✅ 保留不變
├── requirements.txt        ✅ 保留不變
└── .env                    → 需修改
```

### ❌ 需要清理的舊爬蟲（房地產新聞）

```
app/services/crawler/
├── bharian_crawler.py          ❌ 刪除 (馬來西亞房產)
├── ebc_crawler.py              ❌ 刪除 (東森房產)
├── edgeprop_crawler.py         ❌ 刪除 (EdgeProp 房產)
├── ettoday_crawler.py          ❌ 刪除 (ETtoday 房產)
├── freemalaysiatoday_crawler.py ❌ 刪除 (馬來西亞房產)
├── hk852house_crawler.py       ❌ 刪除 (香港房產)
├── ltn_crawler.py              ❌ 刪除 (自由時報房產)
├── nextapple_crawler.py        ❌ 刪除 (蘋果地產)
├── starproperty_crawler.py     ❌ 刪除 (Star Property 房產)
└── udn_crawler.py              ❌ 刪除 (聯合報房產)
```

### ✨ 需要新增的 Yahoo Sports 爬蟲

```
app/services/crawler/
├── base.py                      ✅ 已存在（保留）
├── npb_crawler.py              🆕 新增 (日本職棒)
├── mlb_crawler.py              🆕 新增 (美國大聯盟)
├── hsb_crawler.py              🆕 新增 (高校野球)
├── bbl_crawler.py              🆕 新增 (大學野球)
├── ind_crawler.py              🆕 新增 (獨立聯盟)
└── amateur_crawler.py          🆕 新增 (業餘棒球)
```

---

## 🎯 遷移步驟

### Phase 1: 清理舊爬蟲 ✂️

#### 步驟 1.1：刪除舊爬蟲文件

```bash
# 刪除所有房地產爬蟲
cd app/services/crawler/
rm bharian_crawler.py
rm ebc_crawler.py
rm edgeprop_crawler.py
rm ettoday_crawler.py
rm freemalaysiatoday_crawler.py
rm hk852house_crawler.py
rm ltn_crawler.py
rm nextapple_crawler.py
rm starproperty_crawler.py
rm udn_crawler.py

# 保留
# - base.py
# - __init__.py
```

#### 步驟 1.2：清理其他相關文件

```bash
# 刪除 debug 文件
rm debug_ettoday.py
rm debug_ettoday_article.html
rm debug_ettoday_output.html

# 清理日誌（可選）
rm -rf logs/*

# 清理舊的優化文檔（如果有衝突）
# OPTIMIZATION_SUMMARY.md 可以保留或刪除
```

---

### Phase 2: 更新配置 ⚙️

#### 步驟 2.1：更新 `app/core/config.py`

```python
# app/core/config.py

import os
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    # 專案基本設定
    PROJECT_NAME: str = "Sportsnavi API"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # Yahoo Sports 來源設定
    NEWS_SOURCES: Dict[str, Dict[str, Any]] = {
        "npb": {
            "name": "日本職棒 NPB",
            "base_url": "https://baseball.yahoo.co.jp/npb/"
        },
        "mlb": {
            "name": "美國大聯盟 MLB",
            "base_url": "https://baseball.yahoo.co.jp/mlb/"
        },
        "hsb": {
            "name": "高校野球",
            "base_url": "https://baseball.yahoo.co.jp/hsb/"
        },
        "bbl": {
            "name": "大學野球",
            "base_url": "https://baseball.yahoo.co.jp/bbl/"
        },
        "ind": {
            "name": "獨立聯盟",
            "base_url": "https://baseball.yahoo.co.jp/ind/"
        },
        "amateur": {
            "name": "業餘棒球",
            "base_url": "https://baseball.yahoo.co.jp/amateur/"
        }
    }

    # 資料庫設定
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "db"
    POSTGRES_DB: str = "sportsnavidb"  # ← 改名
    DATABASE_URL: Optional[str] = None

    # Chrome 設定
    CHROME_BIN: str = "/usr/bin/chromium"
    CHROMEDRIVER_PATH: str = "/usr/bin/chromedriver"

    # 爬蟲設定
    CRAWLER_MAX_RETRIES: int = 3
    CRAWLER_TIMEOUT: int = 30
    CRAWLER_DELAY_MIN: int = 1
    CRAWLER_DELAY_MAX: int = 3

    # 記憶體管理（新增）
    MAX_CONCURRENT_CRAWLERS: int = int(os.getenv('MAX_CONCURRENT_CRAWLERS', '3'))
    MAX_RAM_GB: int = 8
    RESERVED_RAM_GB: int = 2

    # 資料保留設定（新增）
    RETENTION_MONTHS: int = 13

    # 日誌設定
    LOG_LEVEL: str = "INFO"

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return (
            f"postgresql://"
            f"{values.get('POSTGRES_USER')}:"
            f"{values.get('POSTGRES_PASSWORD')}@"
            f"{values.get('POSTGRES_SERVER')}/"
            f"{values.get('POSTGRES_DB')}"
        )

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if v == "your-secret-key" or v == "your-secret-key-change-this-in-production":
            raise ValueError("Please change SECRET_KEY in production environment")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

#### 步驟 2.2：更新 `.env` 文件

```bash
# .env

# 專案設定
PROJECT_NAME="Sportsnavi API"
SECRET_KEY="your-secret-key-at-least-32-characters-long-change-this"

# 資料庫設定
POSTGRES_USER=user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_SERVER=db
POSTGRES_DB=sportsnavidb

# 爬蟲設定
MAX_CONCURRENT_CRAWLERS=3
CRAWLER_MAX_RETRIES=3
CRAWLER_TIMEOUT=30

# Chrome 設定
CHROME_HEADLESS=true
DISABLE_IMAGES=true

# 日誌設定
LOG_LEVEL=INFO
```

#### 步驟 2.3：更新 `docker-compose.yml`

```yaml
# docker-compose.yml

version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: sportsnavi-db
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: sportsnavidb  # ← 改名
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    deploy:
      resources:
        limits:
          memory: 1.5G
        reservations:
          memory: 512M
    command:
      - "postgres"
      - "-c"
      - "shared_buffers=256MB"
      - "-c"
      - "max_connections=50"

  web:
    build: .
    container_name: sportsnavi-web
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_SERVER=db
      - POSTGRES_DB=sportsnavidb
      - SECRET_KEY=${SECRET_KEY}
      - MAX_CONCURRENT_CRAWLERS=3
    deploy:
      resources:
        limits:
          memory: 6G
        reservations:
          memory: 2G

volumes:
  postgres_data:
```

---

### Phase 3: 實作 Yahoo Sports 爬蟲 🏗️

#### 步驟 3.1：檢查 `base.py` 是否需要調整

先讀取 `base.py`，確認是否需要修改。

#### 步驟 3.2：創建 NPB 爬蟲範本

```python
# app/services/crawler/npb_crawler.py

from .base import BaseCrawler
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NPBCrawler(BaseCrawler):
    """日本職棒 (NPB) 爬蟲"""

    def __init__(self):
        super().__init__()
        self.source_name = "NPB"
        self.base_url = "https://baseball.yahoo.co.jp/npb/"
        self.needs_javascript = True

    async def crawl_list(self, page: int = 1) -> List[Dict]:
        """
        爬取列表頁

        Returns:
            [
                {
                    'title': '文章標題',
                    'url': '文章URL',
                    'image_url': '圖片URL',
                    'category': 'NPB',
                },
                ...
            ]
        """
        # TODO: 實作列表頁爬取邏輯
        pass

    async def crawl_article(self, article_info: Dict) -> Optional[Dict]:
        """
        爬取文章內容

        Returns:
            {
                'title': '文章標題',
                'content': '文章內容',
                'description': '摘要',
                'published_at': datetime,
                'image_url': '圖片URL',
                'category': 'NPB',
                'reporter': '記者',
            }
        """
        # TODO: 實作文章內容爬取邏輯
        pass
```

#### 步驟 3.3：更新 `test_crawler.py`

```python
# app/tests/test_crawler.py

import asyncio
import sys
from app.services.crawler.npb_crawler import NPBCrawler
from app.services.crawler.mlb_crawler import MLBCrawler
from app.services.crawler.hsb_crawler import HSBCrawler
from app.services.crawler.bbl_crawler import BBLCrawler
from app.services.crawler.ind_crawler import INDCrawler
from app.services.crawler.amateur_crawler import AmateurCrawler
from app.core.database import SessionLocal
from app.models.article import Article
import pytest
from datetime import datetime, timedelta
import argparse
import logging

# 設定日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def get_crawler(crawler_name: str):
    """根據名稱取得對應的爬蟲實例"""
    crawlers = {
        'npb': NPBCrawler(),
        'mlb': MLBCrawler(),
        'hsb': HSBCrawler(),
        'bbl': BBLCrawler(),
        'ind': INDCrawler(),
        'amateur': AmateurCrawler(),
    }
    return crawlers.get(crawler_name)

@pytest.mark.asyncio
async def test_crawler(crawler_type="npb", start_date=None, end_date=None):
    """測試爬蟲"""
    try:
        # 根據參數選擇爬蟲
        crawler = get_crawler(crawler_type.lower())
        if not crawler:
            raise ValueError(f"未知的爬蟲類型: {crawler_type}")

        logger.info(f"開始爬取 {crawler_type} 文章 (日期範圍: {start_date} ~ {end_date})...")

        # 初始化 driver
        if hasattr(crawler, 'setup_driver'):
            crawler.setup_driver()

        try:
            # 執行爬蟲
            articles = await crawler.crawl(start_date=start_date, end_date=end_date)

            logger.info(f"爬取到 {len(articles)} 篇文章")

            # 存入資料庫（使用批次操作）
            db = SessionLocal()
            try:
                from app.core.db_utils import batch_upsert_articles

                # 準備文章資料
                article_data_list = []
                for article in articles:
                    if isinstance(article, dict):
                        article_data = {
                            'url': article.get('url'),
                            'title': article.get('title'),
                            'content': article.get('content'),
                            'published_at': article.get('published_at'),
                            'source': crawler_type.lower(),
                            'image_url': article.get('image_url'),
                            'description': article.get('description'),
                            'category': article.get('category'),
                            'reporter': article.get('reporter'),
                        }
                    else:
                        article_data = {
                            'url': article.url,
                            'title': article.title,
                            'content': article.content,
                            'published_at': article.published_at,
                            'source': crawler_type.lower(),
                            'image_url': article.image_url,
                            'description': article.description,
                            'category': getattr(article, 'category', None),
                            'reporter': getattr(article, 'reporter', None),
                        }
                    article_data_list.append(article_data)

                # 批次 upsert
                saved_count, updated_count = batch_upsert_articles(db, article_data_list, batch_size=50)

                logger.info(f"完成！新增: {saved_count} 篇，更新: {updated_count} 篇")
                return len(articles)

            except Exception as e:
                logger.error(f"資料庫操作失敗: {str(e)}")
                db.rollback()
                raise
            finally:
                db.close()

        finally:
            # 清理資源
            if hasattr(crawler, 'cleanup'):
                crawler.cleanup()

    except Exception as e:
        logger.error(f"爬蟲執行失敗: {str(e)}")
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('crawler',
                       choices=['npb', 'mlb', 'hsb', 'bbl', 'ind', 'amateur'],
                       help='指定要測試的爬蟲')
    parser.add_argument('--start_date',
                       help='回補起始日期 (YYYY-MM-DD)',
                       default='2025-01-07')
    parser.add_argument('--end_date',
                       help='回補結束日期 (YYYY-MM-DD)',
                       default='2025-01-07')
    parser.add_argument('--debug', action='store_true',
                       help='開啟除錯模式')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    asyncio.run(test_crawler(args.crawler, args.start_date, args.end_date))
```

---

### Phase 4: 實作資料保留與記憶體管理 🔧

#### 步驟 4.1：新增資料保留服務

```bash
# 創建新文件
touch app/services/data_retention.py
```

將 `data_retention_policy.md` 中的程式碼複製到這個文件。

#### 步驟 4.2：更新 `main.py` 加入排程器

更新 `app/main.py`，加入：
1. 資料清理排程（每月 1 號凌晨 3:00）
2. 爬蟲排程（每天 4 次）
3. 並發控制（asyncio.Semaphore）

---

### Phase 5: 測試與驗證 ✅

#### 步驟 5.1：清理資料庫（如果需要）

```bash
# 如果要全新開始
docker-compose down -v  # 刪除所有 volumes
docker-compose up -d db  # 只啟動資料庫
```

#### 步驟 5.2：啟動服務

```bash
docker-compose up --build -d
```

#### 步驟 5.3：測試爬蟲

```bash
# 測試單個爬蟲
docker exec sportsnavi-web python -m app.tests.test_crawler npb \
    --start_date 2025-11-01 --end_date 2025-11-03

# 測試資料清理（dry-run）
docker exec sportsnavi-web python -m app.tests.test_cleanup --summary
```

---

## 📋 執行檢查清單

### Phase 1: 清理 ✂️
- [ ] 刪除 10 個舊爬蟲文件
- [ ] 刪除 debug 文件
- [ ] 清理 logs（可選）

### Phase 2: 配置 ⚙️
- [ ] 更新 `config.py`
- [ ] 更新 `.env`
- [ ] 更新 `docker-compose.yml`
- [ ] 檢查 `base.py` 是否需要調整

### Phase 3: 實作爬蟲 🏗️
- [ ] 創建 `npb_crawler.py`
- [ ] 創建 `mlb_crawler.py`
- [ ] 創建 `hsb_crawler.py`
- [ ] 創建 `bbl_crawler.py`
- [ ] 創建 `ind_crawler.py`
- [ ] 創建 `amateur_crawler.py`
- [ ] 更新 `test_crawler.py`

### Phase 4: 進階功能 🔧
- [ ] 創建 `data_retention.py`
- [ ] 更新 `main.py` 加入排程器
- [ ] 創建 `test_cleanup.py`

### Phase 5: 測試 ✅
- [ ] 資料庫遷移（如需要）
- [ ] 啟動服務
- [ ] 測試單個爬蟲
- [ ] 測試資料清理
- [ ] 測試 Web UI

---

## ⚠️ 注意事項

1. **備份**：如果 reas 專案還在使用，建議先備份
2. **資料庫**：新專案使用新的資料庫名稱（`sportsnavidb`）
3. **測試**：每個階段完成後都要測試
4. **漸進式**：不需要一次實作所有 6 個爬蟲，可以先做 NPB

---

## 🚀 快速開始（最小可行版本）

如果想最快啟動，可以：

1. **只清理爬蟲文件**（10 個舊爬蟲）
2. **只更新 config.py 和 .env**
3. **只實作 1 個爬蟲**（NPB）
4. **測試能否運行**

其他功能（資料清理、記憶體管理、其他爬蟲）可以後續再加。

---

**預計時間**：
- Phase 1-2: 30 分鐘
- Phase 3 (1 個爬蟲): 2-4 小時
- Phase 4: 1 小時
- Phase 5: 30 分鐘

**總計**: 約 4-6 小時（實作 1 個爬蟲的情況）
