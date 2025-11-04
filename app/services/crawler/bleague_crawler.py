from .baseball_crawler import BaseballCrawler

class BLeagueCrawler(BaseballCrawler):
    """Bリーグ爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='bleague',
            base_url='https://sports.yahoo.co.jp/basket/bleague/',
            category_name='Bリーグ'
        )
