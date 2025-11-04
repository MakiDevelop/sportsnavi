# 記憶體優化配置（8GB RAM 限制）

## 問題分析

- **每個 Chrome 實例**：500MB - 1GB RAM
- **8 個 Agent 並行**：4-8GB RAM
- **系統其他服務**：PostgreSQL (500MB), FastAPI (200MB), OS (1GB)
- **總需求**：約 6-10GB → **超出 8GB 限制**

## 解決方案

### 方案 1：限制並行數量（推薦）

```python
# app/core/config.py

import os

class Settings:
    # 記憶體配置
    MAX_CONCURRENT_CRAWLERS = int(os.getenv('MAX_CONCURRENT_CRAWLERS', '3'))

    # Chrome 配置
    CHROME_HEADLESS = True  # 無頭模式節省 20-30% 記憶體
    CHROME_DISABLE_GPU = True
    CHROME_DISABLE_DEV_SHM = True  # 使用磁碟而非共享記憶體

    # 系統配置
    MAX_RAM_GB = 8
    RESERVED_RAM_GB = 2  # 保留給系統和 DB
```

```python
# app/main.py

import asyncio
from app.core.config import Settings

settings = Settings()

async def run_crawler_process(start_date, end_date):
    """使用 Semaphore 限制並行數"""

    sources = ["npb", "mlb", "hsb", "bbl", "ind", "amateur"]  # 棒球各分類

    # 關鍵：限制並發數
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_CRAWLERS)

    async def run_with_limit(source: str):
        async with semaphore:
            logger.info(f"🚀 啟動爬蟲: {source}")
            try:
                count = await test_crawler(source, start_date, end_date)
                logger.info(f"✅ {source} 完成: {count} 篇文章")
                return {source: {'status': 'success', 'count': count}}
            except Exception as e:
                logger.error(f"❌ {source} 失敗: {str(e)}")
                return {source: {'status': 'failed', 'error': str(e)}}

    # 所有任務提交，但同時只運行 MAX_CONCURRENT_CRAWLERS 個
    tasks = [run_with_limit(s) for s in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 統計
    success = sum(1 for r in results if list(r.values())[0]['status'] == 'success')
    logger.info(f"📊 完成: {success}/{len(sources)}")

    return results
```

### 方案 2：優化 Chrome 配置

```python
# app/services/crawler/base.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class BaseCrawler(ABC):
    def setup_driver(self):
        """優化記憶體使用的 Chrome 配置"""
        chrome_options = Options()

        # 基礎配置
        chrome_options.add_argument('--headless=new')  # 新版 headless 模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')  # 重要！

        # 記憶體優化
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # 不載入圖片（節省 30-40%）
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')

        # 效能優化
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')

        # 記憶體限制
        chrome_options.add_argument('--max_old_space_size=512')  # 限制 JS heap
        chrome_options.add_argument('--js-flags=--max-old-space-size=512')

        # User Agent（反爬蟲）
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)

        logger.info(f"✅ Chrome Driver 啟動 (PID: {self.driver.service.process.pid})")

    def cleanup(self):
        """確保資源釋放"""
        if self.driver:
            try:
                pid = self.driver.service.process.pid
                self.driver.quit()
                logger.info(f"🧹 Chrome Driver 已關閉 (PID: {pid})")
            except Exception as e:
                logger.error(f"清理 Driver 時發生錯誤: {e}")
            finally:
                self.driver = None
```

### 方案 3：Docker Compose 記憶體限制

```yaml
# docker-compose.yml

version: '3.8'

services:
  web:
    build: .
    container_name: sportsnavi-web
    ports:
      - "8000:8000"
    environment:
      - MAX_CONCURRENT_CRAWLERS=3
    deploy:
      resources:
        limits:
          memory: 6G  # 6GB 給爬蟲服務
        reservations:
          memory: 2G
    depends_on:
      - db

  db:
    image: postgres:15-alpine  # alpine 版本更省記憶體
    container_name: sportsnavi-db
    environment:
      POSTGRES_DB: sportsnavi
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 1.5G  # 1.5GB 給資料庫
        reservations:
          memory: 512M
    command:
      - "postgres"
      - "-c"
      - "shared_buffers=256MB"  # 限制共享記憶體
      - "-c"
      - "max_connections=50"    # 限制連接數

volumes:
  postgres_data:
```

## 效能預估

### 配置 A：3 個並行（推薦）
- **記憶體使用**：~5-6GB
- **執行時間**：~5-8 分鐘（6 個 Agent）
- **穩定性**：⭐⭐⭐⭐⭐

### 配置 B：4 個並行
- **記憶體使用**：~6.5-7.5GB
- **執行時間**：~4-6 分鐘
- **穩定性**：⭐⭐⭐⭐ (接近極限)

### 配置 C：2 個並行（保守）
- **記憶體使用**：~4-5GB
- **執行時間**：~8-12 分鐘
- **穩定性**：⭐⭐⭐⭐⭐

## 監控腳本

```python
# app/utils/memory_monitor.py

import psutil
import logging

logger = logging.getLogger(__name__)

class MemoryMonitor:
    @staticmethod
    def check_available_memory() -> float:
        """返回可用記憶體（GB）"""
        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024 ** 3)
        return available_gb

    @staticmethod
    def should_start_crawler() -> bool:
        """檢查是否有足夠記憶體啟動新爬蟲"""
        available = MemoryMonitor.check_available_memory()
        threshold = 1.5  # 至少保留 1.5GB

        if available < threshold:
            logger.warning(f"⚠️ 記憶體不足: {available:.2f}GB < {threshold}GB")
            return False

        return True

    @staticmethod
    def log_memory_usage():
        """記錄當前記憶體使用"""
        mem = psutil.virtual_memory()
        logger.info(
            f"📊 記憶體使用: {mem.percent}% "
            f"({mem.used / (1024**3):.2f}GB / {mem.total / (1024**3):.2f}GB)"
        )

# 使用範例
async def run_single_crawler(source: str):
    if not MemoryMonitor.should_start_crawler():
        logger.error(f"跳過 {source}：記憶體不足")
        return {'status': 'skipped', 'reason': 'insufficient_memory'}

    MemoryMonitor.log_memory_usage()
    # ... 執行爬蟲
```

## 測試與調整

```bash
# 1. 測試單個爬蟲的記憶體使用
docker stats sportsnavi-web --no-stream

# 2. 測試不同並行數
# 設定 MAX_CONCURRENT_CRAWLERS=2
docker-compose up -d
# 觀察記憶體使用

# 3. 壓力測試
docker exec sportsnavi-web python -m app.tests.stress_test
```

## 建議部署配置

```bash
# .env
MAX_CONCURRENT_CRAWLERS=3  # 生產環境建議 3
CHROME_HEADLESS=true
DISABLE_IMAGES=true  # 不載入圖片，節省記憶體
```

**總結**：推薦使用 **3 個並行 + Chrome 記憶體優化**，可在 8GB RAM 下穩定運行。
