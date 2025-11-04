from .baseball_crawler import BaseballCrawler

class TableTennisCrawler(BaseballCrawler):
    """卓球爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='tabletennis',
            base_url='https://sports.yahoo.co.jp/tabletennis/',
            category_name='卓球'
        )
