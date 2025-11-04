from .baseball_crawler import BaseballCrawler

class FightCrawler(BaseballCrawler):
    """格闘技爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='fight',
            base_url='https://sports.yahoo.co.jp/fight/',
            category_name='格闘技'
        )
