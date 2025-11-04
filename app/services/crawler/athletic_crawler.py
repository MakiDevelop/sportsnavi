from .baseball_crawler import BaseballCrawler

class AthleticCrawler(BaseballCrawler):
    """陸上爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='athletic',
            base_url='https://sports.yahoo.co.jp/athletic/',
            category_name='陸上'
        )
