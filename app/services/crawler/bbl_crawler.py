from .baseball_crawler import BaseballCrawler

class BBLCrawler(BaseballCrawler):
    """大學野球爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='bbl',
            base_url='https://baseball.yahoo.co.jp/bbl/',
            category_name='大學野球'
        )
