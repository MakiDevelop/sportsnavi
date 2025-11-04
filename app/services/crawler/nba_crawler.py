from .baseball_crawler import BaseballCrawler

class NBACrawler(BaseballCrawler):
    """NBA爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='nba',
            base_url='https://sports.yahoo.co.jp/basket/nba/',
            category_name='NBA'
        )
