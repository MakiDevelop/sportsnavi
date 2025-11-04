from .baseball_crawler import BaseballCrawler

class BasketJapanCrawler(BaseballCrawler):
    """バスケ代表爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='basket_japan',
            base_url='https://sports.yahoo.co.jp/basket/japan/',
            category_name='バスケ代表'
        )
