from .baseball_crawler import BaseballCrawler

class OtherSportsCrawler(BaseballCrawler):
    """他競技爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='other',
            base_url='https://sports.yahoo.co.jp/other/',
            category_name='他競技'
        )
