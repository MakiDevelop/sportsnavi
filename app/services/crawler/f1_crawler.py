from .baseball_crawler import BaseballCrawler

class F1Crawler(BaseballCrawler):
    """F1爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='f1',
            base_url='https://sports.yahoo.co.jp/f1/',
            category_name='F1'
        )
