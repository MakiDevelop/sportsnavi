from .baseball_crawler import BaseballCrawler

class WorldSoccerCrawler(BaseballCrawler):
    """海外サッカー爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='ws',
            base_url='https://soccer.yahoo.co.jp/ws/',
            category_name='海外サッカー'
        )
