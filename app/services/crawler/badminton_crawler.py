from .baseball_crawler import BaseballCrawler

class BadmintonCrawler(BaseballCrawler):
    """バドミントン爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='badminton',
            base_url='https://sports.yahoo.co.jp/badminton/',
            category_name='バドミントン'
        )
