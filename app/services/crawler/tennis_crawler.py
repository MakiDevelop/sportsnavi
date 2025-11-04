from .baseball_crawler import BaseballCrawler

class TennisCrawler(BaseballCrawler):
    """テニス爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='tennis',
            base_url='https://sports.yahoo.co.jp/tennis/',
            category_name='テニス'
        )
