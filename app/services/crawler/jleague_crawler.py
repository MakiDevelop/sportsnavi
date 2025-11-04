from .baseball_crawler import BaseballCrawler

class JLeagueCrawler(BaseballCrawler):
    """Jリーグ爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='jleague',
            base_url='https://soccer.yahoo.co.jp/jleague/',
            category_name='Jリーグ'
        )
