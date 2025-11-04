import asyncio
import sys
# Baseball crawlers
from app.services.crawler.npb_crawler import NPBCrawler
from app.services.crawler.mlb_crawler import MLBCrawler
from app.services.crawler.hsb_crawler import HSBCrawler
from app.services.crawler.bbl_crawler import BBLCrawler
from app.services.crawler.ipbl_crawler import IPBLCrawler
from app.services.crawler.amateur_crawler import AmateurCrawler
from app.services.crawler.baseball_japan_crawler import BaseballJapanCrawler

# Soccer crawlers
from app.services.crawler.jleague_crawler import JLeagueCrawler
from app.services.crawler.ws_crawler import WorldSoccerCrawler
from app.services.crawler.soccer_japan_crawler import SoccerJapanCrawler
from app.services.crawler.youth_soccer_crawler import YouthSoccerCrawler

# Racing crawlers
from app.services.crawler.keiba_crawler import KeibaCrawler
from app.services.crawler.boatrace_crawler import BoatraceCrawler

# Combat & Winter sports crawlers
from app.services.crawler.sumo_crawler import SumoCrawler
from app.services.crawler.figureskate_crawler import FigureSkateCrawler
from app.services.crawler.curling_crawler import CurlingCrawler
from app.services.crawler.fight_crawler import FightCrawler

# Racquet sports crawlers
from app.services.crawler.golf_crawler import GolfCrawler
from app.services.crawler.tennis_crawler import TennisCrawler
from app.services.crawler.tabletennis_crawler import TableTennisCrawler
from app.services.crawler.badminton_crawler import BadmintonCrawler

# Team sports crawlers
from app.services.crawler.f1_crawler import F1Crawler
from app.services.crawler.volley_crawler import VolleyCrawler
from app.services.crawler.rugby_crawler import RugbyCrawler
from app.services.crawler.athletic_crawler import AthleticCrawler

# Basketball crawlers
from app.services.crawler.bleague_crawler import BLeagueCrawler
from app.services.crawler.nba_crawler import NBACrawler
from app.services.crawler.basket_japan_crawler import BasketJapanCrawler
from app.services.crawler.youth_basket_crawler import YouthBasketCrawler

# Other sports crawlers
from app.services.crawler.other_crawler import OtherSportsCrawler
from app.services.crawler.dosports_crawler import DoSportsCrawler

from app.core.database import SessionLocal
from app.models.article import Article
import pytest
from datetime import datetime, timedelta
import argparse
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 設定日誌格式
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s [%(levelname)s] %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# 資料庫連線設定
# 注意：容器內使用 db:5432，主機連接使用 localhost:5433
DATABASE_URL = "postgresql://user:sportsnavi_password_2024@db:5432/sportsnavidb"

def get_crawler(crawler_name: str):
	"""根據名稱取得對應的爬蟲實例"""
	crawlers = {
		# Baseball
		'npb': NPBCrawler(),
		'mlb': MLBCrawler(),
		'hsb': HSBCrawler(),
		'bbl': BBLCrawler(),
		'ipbl': IPBLCrawler(),
		'amateur': AmateurCrawler(),
		'baseball_japan': BaseballJapanCrawler(),

		# Soccer
		'jleague': JLeagueCrawler(),
		'ws': WorldSoccerCrawler(),
		'soccer_japan': SoccerJapanCrawler(),
		'youth_soccer': YouthSoccerCrawler(),

		# Racing
		'keiba': KeibaCrawler(),
		'boatrace': BoatraceCrawler(),

		# Combat & Winter
		'sumo': SumoCrawler(),
		'figureskate': FigureSkateCrawler(),
		'curling': CurlingCrawler(),
		'fight': FightCrawler(),

		# Racquet
		'golf': GolfCrawler(),
		'tennis': TennisCrawler(),
		'tabletennis': TableTennisCrawler(),
		'badminton': BadmintonCrawler(),

		# Team sports
		'f1': F1Crawler(),
		'volley': VolleyCrawler(),
		'rugby': RugbyCrawler(),
		'athletic': AthleticCrawler(),

		# Basketball
		'bleague': BLeagueCrawler(),
		'nba': NBACrawler(),
		'basket_japan': BasketJapanCrawler(),
		'youth_basket': YouthBasketCrawler(),

		# Other
		'other': OtherSportsCrawler(),
		'dosports': DoSportsCrawler(),
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

		# 執行爬蟲（所有爬蟲都使用統一的 crawl 方法）
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

	except Exception as e:
		logger.error(f"爬蟲執行失敗: {str(e)}")
		raise

async def crawl_historical_data(start_date=None, end_date=None):
	"""回補指定日期範圍的文章"""
	if not start_date:
		start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
	if not end_date:
		end_date = datetime.now().strftime('%Y-%m-%d')

	logging.info(f"開始回補歷史文章 ({start_date} ~ {end_date})...")

	try:
		# 依序執行所有爬蟲
		all_crawlers = [
			# Baseball
			'npb', 'mlb', 'hsb', 'bbl', 'ipbl', 'amateur', 'baseball_japan',
			# Soccer
			'jleague', 'ws', 'soccer_japan', 'youth_soccer',
			# Racing
			'keiba', 'boatrace',
			# Combat & Winter
			'sumo', 'figureskate', 'curling', 'fight',
			# Racquet
			'golf', 'tennis', 'tabletennis', 'badminton',
			# Team sports
			'f1', 'volley', 'rugby', 'athletic',
			# Basketball
			'bleague', 'nba', 'basket_japan', 'youth_basket',
			# Other
			'other', 'dosports',
		]

		for crawler_name in all_crawlers:
			logging.info(f"開始執行 {crawler_name.upper()} 爬蟲...")
			count = await test_crawler(crawler_name, start_date, end_date)
			logging.info(f"{crawler_name.upper()} 爬蟲完成，共取得 {count} 篇文章")

		logging.info("所有爬蟲執行完成")

	except Exception as e:
		logging.error(f"回補程序執行失敗: {str(e)}")
		raise

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	# 所有可用的爬蟲
	available_crawlers = [
		# Baseball
		'npb', 'mlb', 'hsb', 'bbl', 'ipbl', 'amateur', 'baseball_japan',
		# Soccer
		'jleague', 'ws', 'soccer_japan', 'youth_soccer',
		# Racing
		'keiba', 'boatrace',
		# Combat & Winter
		'sumo', 'figureskate', 'curling', 'fight',
		# Racquet
		'golf', 'tennis', 'tabletennis', 'badminton',
		# Team sports
		'f1', 'volley', 'rugby', 'athletic',
		# Basketball
		'bleague', 'nba', 'basket_japan', 'youth_basket',
		# Other
		'other', 'dosports',
	]

	parser.add_argument('crawler',
					   choices=available_crawlers,
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
