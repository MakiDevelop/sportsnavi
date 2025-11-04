from .baseball_crawler import BaseballCrawler

class YouthBasketCrawler(BaseballCrawler):
    """学生バスケ爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='youth_basket',
            base_url='https://sports.yahoo.co.jp/basket/youth/',
            category_name='学生バスケ'
        )
