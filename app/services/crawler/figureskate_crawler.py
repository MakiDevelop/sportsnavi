from .baseball_crawler import BaseballCrawler

class FigureSkateCrawler(BaseballCrawler):
    """フィギュア爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='figureskate',
            base_url='https://sports.yahoo.co.jp/figureskate/',
            category_name='フィギュア'
        )
