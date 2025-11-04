from .baseball_crawler import BaseballCrawler

class SoccerJapanCrawler(BaseballCrawler):
    """サッカー代表爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='soccer_japan',
            base_url='https://soccer.yahoo.co.jp/japan/',
            category_name='サッカー代表'
        )
