from .baseball_crawler import BaseballCrawler

class YouthSoccerCrawler(BaseballCrawler):
    """高校年代爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='youth_soccer',
            base_url='https://soccer.yahoo.co.jp/youth/',
            category_name='高校年代'
        )
