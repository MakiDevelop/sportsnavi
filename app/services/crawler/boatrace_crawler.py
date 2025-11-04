from .baseball_crawler import BaseballCrawler

class BoatraceCrawler(BaseballCrawler):
    """ボートレース爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='boatrace',
            base_url='https://sports.yahoo.co.jp/boatrace/',
            category_name='ボートレース'
        )
