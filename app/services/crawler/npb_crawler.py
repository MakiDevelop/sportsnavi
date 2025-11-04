from .baseball_crawler import BaseballCrawler

class NPBCrawler(BaseballCrawler):
    """日本職棒 (NPB) 爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='npb',
            base_url='https://baseball.yahoo.co.jp/npb/',
            category_name='NPB'
        )
