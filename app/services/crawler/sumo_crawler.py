from .baseball_crawler import BaseballCrawler

class SumoCrawler(BaseballCrawler):
    """大相撲爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='sumo',
            base_url='https://sports.yahoo.co.jp/sumo/',
            category_name='大相撲'
        )
