from .base import BaseCrawler
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import time
import random
import json
import re

logger = logging.getLogger(__name__)

class BaseballCrawler(BaseCrawler):
    """
    通用棒球新聞爬蟲

    支援所有 Yahoo Sports 棒球分類：
    - NPB (日本職棒)
    - MLB (美國大聯盟)
    - HSB (高校野球)
    - BBL (大學野球)
    - IND (獨立聯盟)
    - Amateur (業餘棒球)
    """

    def __init__(self, source_name: str, base_url: str, category_name: str):
        """
        Args:
            source_name: 資料來源名稱（例如：'npb', 'mlb'）
            base_url: 基礎 URL（例如：'https://baseball.yahoo.co.jp/npb/'）
            category_name: 分類顯示名稱（例如：'NPB', 'MLB'）
        """
        super().__init__()
        self.source_name = source_name
        self.base_url = base_url
        self.category_name = category_name
        self.needs_javascript = True  # Yahoo 網站需要 JavaScript

    async def crawl_list(self, page: int = 1) -> List[Dict]:
        """
        爬取列表頁（包含「ピックアップ」和「新着記事」兩個區域）

        Args:
            page: 頁碼（目前只爬首頁，page 參數保留供未來擴展）

        Returns:
            文章列表
        """
        try:
            list_url = self.base_url
            logger.info(f"開始爬取 {self.category_name} 列表頁: {list_url}")

            # 載入頁面
            self.wait_and_get(list_url)

            # 等待內容載入
            time.sleep(random.uniform(3, 5))

            # 取得頁面 HTML
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            articles = []

            # 1. 爬取「ピックアップ」區域
            pickup_articles = self._crawl_pickup_section(soup)
            articles.extend(pickup_articles)
            logger.info(f"「ピックアップ」區域找到 {len(pickup_articles)} 篇文章")

            # 2. 爬取「新着記事」區域
            timeline_articles = self._crawl_timeline_section(soup)
            articles.extend(timeline_articles)
            logger.info(f"「新着記事」區域找到 {len(timeline_articles)} 篇文章")

            logger.info(f"列表頁共找到 {len(articles)} 篇文章")
            return articles

        except Exception as e:
            logger.error(f"爬取列表頁失敗: {str(e)}")
            return []

    def _crawl_pickup_section(self, soup: BeautifulSoup) -> List[Dict]:
        """爬取「ピックアップ」區域"""
        articles = []

        try:
            # 找到 ピックアップ 區域（嘗試多種選擇器）
            pickup_section = soup.select_one('.sn-modListPickupAdvanced')
            if not pickup_section:
                pickup_section = soup.select_one('.io-modPickup')

            if not pickup_section:
                logger.warning("未找到「ピックアップ」區域")
                return articles

            # 找到所有文章項目
            items = pickup_section.select('.sn-articlePickup')
            if not items:
                items = pickup_section.select('.io-pickup__item')

            for item in items:
                try:
                    # 提取標題和 URL
                    title_elem = item.select_one('.sn-articlePickup__title a')
                    if not title_elem:
                        title_elem = item.select_one('.io-pickup__title a')

                    if not title_elem:
                        continue

                    title = title_elem.text.strip()
                    url = title_elem.get('href', '')

                    # 確保 URL 是完整的
                    if url and not url.startswith('http'):
                        if url.startswith('/'):
                            url = f"https://baseball.yahoo.co.jp{url}"
                        else:
                            url = f"https://baseball.yahoo.co.jp/{url}"

                    # 提取圖片（嘗試多種方式）
                    image_url = ''

                    # 方式1：直接 img 標籤
                    img_elem = item.select_one('img')
                    if img_elem:
                        image_url = img_elem.get('src', '') or img_elem.get('data-src', '')

                    # 方式2：背景圖（如果沒找到 img）
                    if not image_url:
                        style_elem = item.select_one('[style*="background"]')
                        if style_elem:
                            style = style_elem.get('style', '')
                            match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                            if match:
                                image_url = match.group(1)

                    # 提取發佈來源
                    source_elem = item.select_one('.sn-articlePickup__credit')
                    if not source_elem:
                        source_elem = item.select_one('.io-pickup__caption')
                    if not source_elem:
                        source_elem = item.select_one('.io-pickup__copyright')
                    news_source = source_elem.text.strip() if source_elem else ''

                    if not title or not url:
                        logger.warning(f"文章資訊不完整，跳過: title={title}, url={url}")
                        continue

                    articles.append({
                        'title': title,
                        'url': url,
                        'image_url': image_url,
                        'news_source': news_source,
                        'category': self.category_name,
                        'section': 'ピックアップ'
                    })

                    logger.debug(f"[ピックアップ] {title[:30]}... ({news_source})")

                except Exception as e:
                    logger.error(f"解析 ピックアップ 文章項目失敗: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"爬取「ピックアップ」區域失敗: {str(e)}")

        return articles

    def _crawl_timeline_section(self, soup: BeautifulSoup) -> List[Dict]:
        """爬取「新着記事」區域"""
        articles = []

        try:
            # 找到 新着記事 區域
            timeline_section = soup.select_one('.sn-modTimeLine')
            if not timeline_section:
                logger.warning("未找到「新着記事」區域")
                return articles

            # 找到所有文章項目
            items = timeline_section.select('.sn-timeLine__item')

            for item in items:
                try:
                    # 提取 URL（從 a 標籤）
                    link_elem = item.select_one('.sn-timeLine__itemArticleLink')
                    if not link_elem:
                        continue

                    url = link_elem.get('href', '')

                    # 確保 URL 是完整的
                    if url and not url.startswith('http'):
                        if url.startswith('/'):
                            url = f"https://baseball.yahoo.co.jp{url}"
                        else:
                            url = f"https://baseball.yahoo.co.jp/{url}"

                    # 提取標題
                    title_elem = item.select_one('.sn-timeLine__itemTitle')
                    title = title_elem.text.strip() if title_elem else ''

                    # 提取圖片（嘗試多種方式）
                    image_url = ''

                    # 方式1：直接 img 標籤
                    img_elem = item.select_one('img')
                    if img_elem:
                        image_url = img_elem.get('src', '') or img_elem.get('data-src', '')

                    # 方式2：背景圖（從 thumbnail 元素）
                    if not image_url:
                        thumb_elem = item.select_one('.sn-timeLine__itemThumbnail')
                        if thumb_elem:
                            style = thumb_elem.get('style', '')
                            match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                            if match:
                                image_url = match.group(1)

                    # 方式3：視頻縮圖
                    if not image_url:
                        video_thumb = item.select_one('.sn-timeLine__itemVideoThumbnailImg')
                        if video_thumb:
                            style = video_thumb.get('style', '')
                            match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                            if match:
                                image_url = match.group(1)

                    # 提取發佈來源
                    source_elem = item.select_one('.sn-timeLine__itemCredit')
                    news_source = source_elem.text.strip() if source_elem else ''

                    # 提取時間
                    time_elem = item.select_one('.sn-timeLine__itemTime')
                    time_text = time_elem.text.strip() if time_elem else ''

                    # 解析時間
                    published_at = None
                    if time_text:
                        published_at = self._parse_japanese_datetime(time_text)

                    if not title or not url:
                        logger.warning(f"文章資訊不完整，跳過: title={title}, url={url}")
                        continue

                    articles.append({
                        'title': title,
                        'url': url,
                        'image_url': image_url,
                        'news_source': news_source,
                        'published_at': published_at,
                        'category': self.category_name,
                        'section': '新着記事'
                    })

                    logger.debug(f"[新着記事] {title[:30]}... ({news_source}, {time_text})")

                except Exception as e:
                    logger.error(f"解析 新着記事 文章項目失敗: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"爬取「新着記事」區域失敗: {str(e)}")

        return articles

    def _parse_japanese_datetime(self, time_text: str) -> Optional[datetime]:
        """
        解析日文日期時間格式
        支援兩種格式：
        1. 「11/3(月) 12:00」→ datetime(2025, 11, 3, 12, 0)
        2. 「2025/11/4 11:56」→ datetime(2025, 11, 4, 11, 56)
        """
        try:
            # 移除星期幾（例如：(月)、(火)）
            time_text = re.sub(r'\([^)]+\)', '', time_text).strip()

            current_year = datetime.now().year

            # 嘗試解析
            if ' ' in time_text:
                date_part, time_part = time_text.split(' ', 1)
                date_components = date_part.split('/')

                # 判斷格式：YYYY/MM/DD 或 MM/DD
                if len(date_components) == 3:
                    # 格式：2025/11/4 11:56
                    year, month, day = map(int, date_components)
                elif len(date_components) == 2:
                    # 格式：11/4 11:56
                    year = current_year
                    month, day = map(int, date_components)
                else:
                    logger.warning(f"無法識別的日期格式: {date_part}")
                    return None

                hour, minute = map(int, time_part.split(':'))
                return datetime(year, month, day, hour, minute)
            else:
                # 只有日期，沒有時間
                date_components = time_text.split('/')

                if len(date_components) == 3:
                    # 格式：2025/11/4
                    year, month, day = map(int, date_components)
                elif len(date_components) == 2:
                    # 格式：11/4
                    year = current_year
                    month, day = map(int, date_components)
                else:
                    logger.warning(f"無法識別的日期格式: {time_text}")
                    return None

                return datetime(year, month, day)

        except Exception as e:
            logger.warning(f"無法解析日期: {time_text}, 錯誤: {str(e)}")
            return None

    async def crawl_article(self, article_info: Dict) -> Optional[Dict]:
        """
        爬取文章內容

        Args:
            article_info: 從 crawl_list 返回的文章資訊

        Returns:
            完整文章資料
        """
        url = article_info.get('url')

        try:
            logger.info(f"開始爬取文章: {url}")

            # 載入文章頁面
            self.wait_and_get(url)

            # 等待內容載入
            time.sleep(random.uniform(2, 3))

            # 取得頁面 HTML
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # 嘗試從 JSON 資料中提取內容（Yahoo News 使用此方式）
            article_data = self._extract_from_json(soup, article_info)

            if article_data:
                logger.info(f"成功爬取文章（JSON）: {article_data['title'][:30]}... ({len(article_data.get('content', ''))} 字)")
                return article_data

            # 如果 JSON 解析失敗，嘗試從 HTML 提取
            article_data = self._extract_from_html(soup, article_info)

            if article_data:
                logger.info(f"成功爬取文章（HTML）: {article_data['title'][:30]}... ({len(article_data.get('content', ''))} 字)")
                return article_data

            logger.warning(f"無法提取文章內容: {url}")
            return None

        except Exception as e:
            logger.error(f"爬取文章失敗 {url}: {str(e)}")
            return None

    def _extract_from_json(self, soup: BeautifulSoup, article_info: Dict) -> Optional[Dict]:
        """從頁面的 JSON 資料中提取文章內容"""
        try:
            # 找到包含 __PRELOADED_STATE__ 的 script 標籤
            scripts = soup.find_all('script')

            for script in scripts:
                if script.string and '__PRELOADED_STATE__' in script.string:
                    # 提取 JSON 資料
                    script_content = script.string

                    # 找到 JSON 開始的位置
                    start = script_content.find('{')
                    end = script_content.rfind('}') + 1

                    if start == -1 or end == 0:
                        continue

                    json_str = script_content[start:end]
                    data = json.loads(json_str)

                    # 提取文章詳情
                    article_detail = data.get('articleDetail', {})

                    if not article_detail:
                        continue

                    # 提取標題
                    title = article_detail.get('headline', article_info.get('title', ''))

                    # 提取發佈日期
                    create_date = article_detail.get('createDate', {})
                    date_str = create_date.get('date', '')
                    time_str = create_date.get('time', '')

                    published_at = None
                    if date_str and time_str:
                        datetime_str = f"{date_str} {time_str}"
                        published_at = self._parse_japanese_datetime(datetime_str)

                    if not published_at and article_info.get('published_at'):
                        published_at = article_info.get('published_at')

                    if not published_at:
                        published_at = datetime.now()

                    # 提取圖片（多種來源）
                    image_url = article_info.get('image_url', '')

                    # 嘗試從 thumbnail 取得
                    if not image_url:
                        thumbnail = article_detail.get('thumbnail', {})
                        if isinstance(thumbnail, dict):
                            image_url = thumbnail.get('url', '')
                        elif isinstance(thumbnail, str):
                            image_url = thumbnail

                    # 嘗試從 images 陣列取得第一張
                    if not image_url:
                        images = article_detail.get('images', [])
                        if images and len(images) > 0:
                            if isinstance(images[0], dict):
                                image_url = images[0].get('url', '')
                            elif isinstance(images[0], str):
                                image_url = images[0]

                    # 提取內容（從 paragraphs 陣列）
                    paragraphs = article_detail.get('paragraphs', [])
                    content_parts = []

                    for para in paragraphs:
                        if isinstance(para, dict):
                            text = para.get('text', '')
                            if text:
                                content_parts.append(text)
                        elif isinstance(para, str):
                            content_parts.append(para)

                    content = '\n\n'.join(content_parts)

                    # 清理內容
                    content = self.clean_content(content)

                    if not content:
                        logger.warning("從 JSON 提取的內容為空")
                        return None

                    # 提取發佈來源
                    media = article_detail.get('media', {})
                    news_source = media.get('mediaName', article_info.get('news_source', ''))

                    # 提取描述
                    description = content[:200] + '...' if len(content) > 200 else content

                    return {
                        'url': article_info.get('url'),
                        'title': title,
                        'content': content,
                        'description': description,
                        'published_at': published_at,
                        'image_url': image_url,
                        'category': self.category_name,
                        'reporter': None,
                        'source': self.source_name,
                        'news_source': news_source
                    }

        except Exception as e:
            logger.warning(f"從 JSON 提取文章內容失敗: {str(e)}")

        return None

    def _extract_from_html(self, soup: BeautifulSoup, article_info: Dict) -> Optional[Dict]:
        """從 HTML 中提取文章內容（備用方案）"""
        try:
            # 提取標題
            title = article_info.get('title', '')

            # Yahoo News 通常有兩個 h1，第一個是網站 logo，第二個才是文章標題
            h1_tags = soup.select('h1')
            if len(h1_tags) >= 2:
                title = h1_tags[1].text.strip()
            elif len(h1_tags) == 1:
                h1_text = h1_tags[0].text.strip()
                if h1_text != 'Yahoo!ニュース':
                    title = h1_text

            # 如果還是沒有標題，嘗試其他選擇器
            if not title or title == 'Yahoo!ニュース':
                title_selectors = [
                    'title',
                    '[class*="headline"]',
                    '.article-title'
                ]

                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem and title_elem.text.strip():
                        title_text = title_elem.text.strip()
                        if selector == 'title':
                            title_text = title_text.split(' - Yahoo!ニュース')[0]
                            title_text = title_text.split('（')[0]
                        if title_text and title_text != 'Yahoo!ニュース':
                            title = title_text
                            break

            # 提取圖片
            image_url = article_info.get('image_url', '')

            if not image_url:
                article_img = soup.select_one('article img')
                if article_img:
                    image_url = article_img.get('src', '') or article_img.get('data-src', '')

            if not image_url:
                all_imgs = soup.select('img')
                for img in all_imgs:
                    src = img.get('src', '') or img.get('data-src', '')
                    if src and ('newsatcl' in src or 'amd-img' in src or 'news' in src):
                        image_url = src
                        break

            # 提取內容
            content_selectors = [
                'article p',
                '.article-body p',
                '.article-content p',
                '.highLightSearchTarget p',
                '[class*="article"] p',
                'p.sc-'
            ]

            paragraphs = []
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    break

            if not paragraphs:
                logger.warning("未找到文章段落")
                return None

            content = '\n\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
            content = self.clean_content(content)

            if not content:
                return None

            published_at = article_info.get('published_at') or datetime.now()
            news_source = article_info.get('news_source', '')

            description = content[:200] + '...' if len(content) > 200 else content

            return {
                'url': article_info.get('url'),
                'title': title,
                'content': content,
                'description': description,
                'published_at': published_at,
                'image_url': image_url,
                'category': self.category_name,
                'reporter': None,
                'source': self.source_name,
                'news_source': news_source
            }

        except Exception as e:
            logger.warning(f"從 HTML 提取文章內容失敗: {str(e)}")

        return None

    async def crawl(self, start_date=None, end_date=None, max_pages=1):
        """
        執行爬蟲主流程

        Args:
            start_date: 起始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)
            max_pages: 最大爬取頁數（目前只爬首頁）

        Returns:
            文章列表
        """
        try:
            self.setup_driver()

            # 轉換日期格式
            if isinstance(start_date, str):
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            else:
                start_date_obj = start_date

            if isinstance(end_date, str):
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                end_date_obj = end_date

            all_articles = []

            logger.info(f"開始爬取 {self.category_name} 新聞 (日期範圍: {start_date} ~ {end_date})")

            # 爬取列表頁
            articles_list = await self.crawl_list(page=1)

            if not articles_list:
                logger.info("沒有找到文章")
                return all_articles

            # 爬取每篇文章的詳細內容
            for article_info in articles_list:
                # 日期過濾
                article_date = article_info.get('published_at')

                if article_date and start_date_obj and end_date_obj:
                    article_date = article_date.date()

                    if article_date < start_date_obj or article_date > end_date_obj:
                        logger.debug(f"文章日期 {article_date} 不在範圍內，跳過")
                        continue

                # 爬取文章詳細內容
                article_data = await self.crawl_article(article_info)

                if article_data:
                    all_articles.append(article_data)
                    logger.info(f"已爬取 {len(all_articles)} 篇文章")

                # 防止請求過快
                time.sleep(random.uniform(1, 2))

            logger.info(f"{self.category_name} 爬蟲完成，共爬取 {len(all_articles)} 篇文章")
            return all_articles

        finally:
            self.cleanup()
