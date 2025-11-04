from .baseball_crawler import BaseballCrawler

class CurlingCrawler(BaseballCrawler):
    """カーリング爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='curling',
            base_url='https://sports.yahoo.co.jp/curling/',
            category_name='カーリング'
        )
