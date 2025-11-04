from .baseball_crawler import BaseballCrawler

class HSBCrawler(BaseballCrawler):
    """高校野球爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='hsb',
            base_url='https://baseball.yahoo.co.jp/hsb/',
            category_name='高校野球'
        )
