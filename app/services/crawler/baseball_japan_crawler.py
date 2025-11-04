from .baseball_crawler import BaseballCrawler

class BaseballJapanCrawler(BaseballCrawler):
    """侍ジャパン（日本國家隊）爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='baseball_japan',
            base_url='https://baseball.yahoo.co.jp/japan/',
            category_name='侍ジャパン'
        )
