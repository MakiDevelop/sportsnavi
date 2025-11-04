from .baseball_crawler import BaseballCrawler

class DoSportsCrawler(BaseballCrawler):
    """Doスポーツ爬蟲"""

    def __init__(self):
        super().__init__(
            source_name='dosports',
            base_url='https://sports.yahoo.co.jp/dosports/',
            category_name='Doスポーツ'
        )
