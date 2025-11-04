from .baseball_crawler import BaseballCrawler

class KeibaCrawler(BaseballCrawler):
    """競馬爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='keiba',
            base_url='https://sports.yahoo.co.jp/keiba/',
            category_name='競馬'
        )
