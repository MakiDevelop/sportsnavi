from .baseball_crawler import BaseballCrawler

class VolleyCrawler(BaseballCrawler):
    """バレーボール爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='volley',
            base_url='https://sports.yahoo.co.jp/volley/',
            category_name='バレーボール'
        )
