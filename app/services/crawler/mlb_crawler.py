from .baseball_crawler import BaseballCrawler

class MLBCrawler(BaseballCrawler):
    """美國大聯盟 (MLB) 爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='mlb',
            base_url='https://baseball.yahoo.co.jp/mlb/',
            category_name='MLB'
        )
