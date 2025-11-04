from .baseball_crawler import BaseballCrawler

class GolfCrawler(BaseballCrawler):
    """ゴルフ爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='golf',
            base_url='https://sports.yahoo.co.jp/golf/',
            category_name='ゴルフ'
        )
