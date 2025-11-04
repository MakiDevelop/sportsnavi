from .baseball_crawler import BaseballCrawler

class AmateurCrawler(BaseballCrawler):
    """業餘棒球爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='amateur',
            base_url='https://baseball.yahoo.co.jp/amateur/',
            category_name='業餘棒球'
        )
