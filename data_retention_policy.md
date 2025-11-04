# 資料保留策略（13 個月）

## 政策說明

- **保留期限**：13 個月
- **清理頻率**：每月 1 號凌晨 3:00
- **清理標準**：`published_at` 早於 13 個月前的文章
- **備份策略**：清理前先備份（可選）

## 實作方案

### 1. 資料庫清理函數

```python
# app/services/data_retention.py

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, delete
import logging

from app.models.article import Article
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

class DataRetentionService:
    """資料保留服務"""

    RETENTION_MONTHS = 13

    @staticmethod
    def calculate_cutoff_date() -> datetime:
        """計算刪除分界日期"""
        now = datetime.now()
        cutoff = now - timedelta(days=RETENTION_MONTHS * 30)
        return cutoff

    @staticmethod
    def get_articles_to_delete(db: Session) -> int:
        """查詢待刪除文章數量"""
        cutoff_date = DataRetentionService.calculate_cutoff_date()

        count = db.query(func.count(Article.id)).filter(
            Article.published_at < cutoff_date
        ).scalar()

        return count

    @staticmethod
    def get_old_articles_summary(db: Session) -> dict:
        """取得待刪除文章的統計摘要"""
        cutoff_date = DataRetentionService.calculate_cutoff_date()

        # 按來源統計
        summary = db.query(
            Article.source,
            func.count(Article.id).label('count')
        ).filter(
            Article.published_at < cutoff_date
        ).group_by(Article.source).all()

        total = sum(item.count for item in summary)

        return {
            'total': total,
            'cutoff_date': cutoff_date,
            'by_source': [{'source': s.source, 'count': s.count} for s in summary]
        }

    @staticmethod
    def delete_old_articles(db: Session, dry_run: bool = False) -> dict:
        """
        刪除超過保留期限的文章

        Args:
            db: 資料庫 session
            dry_run: True 時只統計不刪除（測試用）

        Returns:
            {
                'deleted_count': 123,
                'cutoff_date': '2024-10-03',
                'dry_run': False,
                'by_source': [...]
            }
        """
        cutoff_date = DataRetentionService.calculate_cutoff_date()

        # 取得刪除摘要
        summary = DataRetentionService.get_old_articles_summary(db)

        logger.info(
            f"{'[測試模式] ' if dry_run else ''}準備刪除 {summary['total']} 篇文章"
            f"（早於 {cutoff_date.strftime('%Y-%m-%d')}）"
        )

        for item in summary['by_source']:
            logger.info(f"  - {item['source']}: {item['count']} 篇")

        if dry_run:
            logger.info("🔍 測試模式：不實際刪除")
            return {
                'deleted_count': 0,
                'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
                'dry_run': True,
                'would_delete': summary['total'],
                'by_source': summary['by_source']
            }

        # 實際刪除
        try:
            stmt = delete(Article).where(Article.published_at < cutoff_date)
            result = db.execute(stmt)
            deleted_count = result.rowcount

            db.commit()

            logger.info(f"✅ 成功刪除 {deleted_count} 篇文章")

            return {
                'deleted_count': deleted_count,
                'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
                'dry_run': False,
                'by_source': summary['by_source']
            }

        except Exception as e:
            db.rollback()
            logger.error(f"❌ 刪除失敗: {str(e)}")
            raise

    @staticmethod
    def cleanup_with_backup(db: Session, backup_dir: str = None) -> dict:
        """
        刪除前先備份

        Args:
            backup_dir: 備份目錄路徑，None 表示不備份
        """
        if backup_dir:
            # 匯出到 CSV
            cutoff_date = DataRetentionService.calculate_cutoff_date()

            from pathlib import Path
            import csv

            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)

            backup_file = backup_path / f"articles_backup_{cutoff_date.strftime('%Y%m%d')}.csv"

            # 查詢待刪除的文章
            old_articles = db.query(Article).filter(
                Article.published_at < cutoff_date
            ).all()

            # 寫入 CSV
            with open(backup_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'url', 'title', 'source', 'category', 'published_at', 'created_at'])

                for article in old_articles:
                    writer.writerow([
                        article.id,
                        article.url,
                        article.title,
                        article.source,
                        article.category,
                        article.published_at,
                        article.created_at
                    ])

            logger.info(f"💾 已備份 {len(old_articles)} 篇文章到 {backup_file}")

        # 執行刪除
        return DataRetentionService.delete_old_articles(db, dry_run=False)


def cleanup_old_data(dry_run: bool = False):
    """
    主要清理函數（供排程器呼叫）
    """
    db = SessionLocal()
    try:
        result = DataRetentionService.delete_old_articles(db, dry_run=dry_run)
        return result
    finally:
        db.close()
```

### 2. 排程器配置

```python
# app/main.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from app.services.data_retention import cleanup_old_data

def setup_scheduler():
    """設定定時任務"""

    scheduler = AsyncIOScheduler(timezone=timezone('Asia/Taipei'))

    # 爬蟲任務（每天 4 次）
    for hour in [8, 12, 16, 20]:
        scheduler.add_job(
            crawl_today,
            CronTrigger(hour=hour, minute=0),
            id=f'crawl_{hour}',
            replace_existing=True
        )

    # 資料清理任務（每月 1 號凌晨 3:00）
    scheduler.add_job(
        cleanup_old_data,
        CronTrigger(day=1, hour=3, minute=0),
        id='data_cleanup',
        replace_existing=True,
        kwargs={'dry_run': False}
    )

    scheduler.start()
    logger.info("✅ 排程器已啟動")
    logger.info("  - 爬蟲任務: 每天 8:00, 12:00, 16:00, 20:00")
    logger.info("  - 資料清理: 每月 1 號 03:00")

    return scheduler
```

### 3. 手動清理命令（測試用）

```python
# app/tests/test_cleanup.py

import argparse
from app.services.data_retention import DataRetentionService
from app.core.database import SessionLocal

def main():
    parser = argparse.ArgumentParser(description='測試資料清理')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='測試模式（不實際刪除）'
    )
    parser.add_argument(
        '--backup',
        type=str,
        help='備份目錄路徑'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='只顯示統計，不刪除'
    )

    args = parser.parse_args()

    db = SessionLocal()

    try:
        if args.summary:
            # 只顯示統計
            summary = DataRetentionService.get_old_articles_summary(db)
            print(f"\n📊 待刪除文章統計")
            print(f"總計: {summary['total']} 篇")
            print(f"分界日期: {summary['cutoff_date'].strftime('%Y-%m-%d')}")
            print(f"\n各來源分布:")
            for item in summary['by_source']:
                print(f"  - {item['source']}: {item['count']} 篇")

        elif args.backup:
            # 備份後刪除
            result = DataRetentionService.cleanup_with_backup(db, args.backup)
            print(f"\n✅ 清理完成")
            print(f"已刪除: {result['deleted_count']} 篇")
            print(f"分界日期: {result['cutoff_date']}")

        else:
            # 一般刪除
            result = DataRetentionService.delete_old_articles(db, dry_run=args.dry_run)

            if args.dry_run:
                print(f"\n🔍 測試模式")
                print(f"將刪除: {result['would_delete']} 篇")
            else:
                print(f"\n✅ 已刪除: {result['deleted_count']} 篇")

            print(f"分界日期: {result['cutoff_date']}")

    finally:
        db.close()

if __name__ == '__main__':
    main()
```

### 4. Docker 使用範例

```bash
# 1. 查看待刪除文章統計（不刪除）
docker exec sportsnavi-web python -m app.tests.test_cleanup --summary

# 輸出範例：
# 📊 待刪除文章統計
# 總計: 1,234 篇
# 分界日期: 2023-10-03
#
# 各來源分布:
#   - npb: 456 篇
#   - mlb: 389 篇
#   - hsb: 389 篇

# 2. 測試模式（不實際刪除）
docker exec sportsnavi-web python -m app.tests.test_cleanup --dry-run

# 3. 實際刪除
docker exec sportsnavi-web python -m app.tests.test_cleanup

# 4. 備份後刪除
docker exec sportsnavi-web python -m app.tests.test_cleanup --backup /app/backups
```

### 5. 監控與告警

```python
# app/services/data_retention.py (新增)

class DataRetentionMonitor:
    """監控資料保留狀態"""

    @staticmethod
    def get_retention_stats(db: Session) -> dict:
        """取得資料保留統計"""

        # 最舊文章
        oldest = db.query(Article).order_by(Article.published_at).first()

        # 最新文章
        newest = db.query(Article).order_by(Article.published_at.desc()).first()

        # 總文章數
        total = db.query(func.count(Article.id)).scalar()

        # 資料庫大小（近似）
        # PostgreSQL: SELECT pg_size_pretty(pg_total_relation_size('articles'));

        return {
            'total_articles': total,
            'oldest_article': oldest.published_at if oldest else None,
            'newest_article': newest.published_at if newest else None,
            'date_range_days': (newest.published_at - oldest.published_at).days if oldest and newest else 0
        }

    @staticmethod
    def check_retention_health(db: Session) -> dict:
        """檢查資料保留是否健康"""

        stats = DataRetentionMonitor.get_retention_stats(db)

        # 檢查是否超過 13 個月
        if stats['oldest_article']:
            age_days = (datetime.now() - stats['oldest_article']).days
            max_allowed_days = 13 * 30  # 390 天

            if age_days > max_allowed_days:
                return {
                    'healthy': False,
                    'reason': f'資料超過保留期限 ({age_days} 天 > {max_allowed_days} 天)',
                    'action': '需要執行清理',
                    'stats': stats
                }

        return {
            'healthy': True,
            'stats': stats
        }
```

### 6. API 端點（可選）

```python
# app/api/admin.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.data_retention import DataRetentionService, DataRetentionMonitor

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/retention/stats")
def get_retention_stats(db: Session = Depends(get_db)):
    """取得資料保留統計"""
    return DataRetentionMonitor.get_retention_stats(db)

@router.get("/retention/health")
def check_retention_health(db: Session = Depends(get_db)):
    """檢查資料保留健康狀態"""
    return DataRetentionMonitor.check_retention_health(db)

@router.get("/retention/summary")
def get_cleanup_summary(db: Session = Depends(get_db)):
    """取得待清理文章摘要"""
    return DataRetentionService.get_old_articles_summary(db)

@router.post("/retention/cleanup")
def trigger_cleanup(dry_run: bool = False, db: Session = Depends(get_db)):
    """手動觸發清理（需要管理員權限）"""
    result = DataRetentionService.delete_old_articles(db, dry_run=dry_run)
    return result
```

## 測試檢查清單

- [ ] 測試 `--summary` 查看統計
- [ ] 測試 `--dry-run` 不實際刪除
- [ ] 測試實際刪除功能
- [ ] 測試備份功能
- [ ] 驗證排程器在每月 1 號執行
- [ ] 檢查刪除後資料庫大小變化

## 注意事項

1. **首次執行建議使用 `--dry-run`**，確認無誤後再實際刪除
2. **建議在低峰期執行**（凌晨 3:00）
3. **重要：刪除前先備份**（至少保留最近一次備份）
4. **PostgreSQL VACUUM**：刪除後執行 `VACUUM FULL articles;` 回收空間

## 預期效果

- **資料量控制**：維持在 ~6-8GB（13 個月資料）
- **查詢效能**：刪除舊資料後查詢更快
- **儲存成本**：避免無限增長

**總結**：每月自動清理 + 手動備份機制，確保資料保留在 13 個月內。
