from .baseball_crawler import BaseballCrawler

class IPBLCrawler(BaseballCrawler):
    """独立リーグ爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='ipbl',
            base_url='https://baseball.yahoo.co.jp/ipbl/',
            category_name='独立リーグ'
        )
