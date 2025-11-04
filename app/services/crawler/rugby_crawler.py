from .baseball_crawler import BaseballCrawler

class RugbyCrawler(BaseballCrawler):
    """ラグビー爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='rugby',
            base_url='https://sports.yahoo.co.jp/rugby/',
            category_name='ラグビー'
        )
