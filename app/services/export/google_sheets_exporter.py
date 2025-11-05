import logging
from datetime import datetime, timedelta, date
from typing import List, Callable, Any, Dict, Optional, Union

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytz import timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.article import Article

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
EXPORT_TIMEZONE = timezone("Asia/Taipei")

HEADER_LABELS = {
    "category": "類別",
    "title": "主標",
    "description": "摘要",
    "content": "全文",
    "image_url": "圖1連結",
    "image_url_2": "圖2連結",
}


def _get_credentials() -> Credentials:
    if settings.GOOGLE_SERVICE_ACCOUNT_INFO:
        return Credentials.from_service_account_info(
            settings.GOOGLE_SERVICE_ACCOUNT_INFO,
            scopes=SCOPES,
        )
    if settings.GOOGLE_SERVICE_ACCOUNT_FILE:
        return Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE,
            scopes=SCOPES,
        )
    raise ValueError("Google Sheets 匯出未設定服務帳號憑證")


def _format_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        localized = EXPORT_TIMEZONE.localize(value)
    else:
        localized = value.astimezone(EXPORT_TIMEZONE)
    return localized.strftime("%Y-%m-%d %H:%M:%S")


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return _format_datetime(value)
    return str(value)


def _normalize_target_date(target: Optional[Union[str, date]]) -> date:
    if target is None:
        return datetime.now(EXPORT_TIMEZONE).date()
    if isinstance(target, date):
        return target
    if isinstance(target, str):
        return datetime.strptime(target, "%Y-%m-%d").date()
    raise ValueError("target_date 必須是 date 或 YYYY-MM-DD 字串")


def export_articles_to_sheet(session: Session, target_date: Optional[Union[str, date]] = None) -> int:
    if not settings.GOOGLE_SHEET_ID:
        raise ValueError("未設定 GOOGLE_SHEET_ID，無法匯出資料")

    columns: List[str] = [
        col.strip()
        for col in settings.GOOGLE_EXPORT_COLUMNS.split(",")
        if col.strip()
    ]
    if not columns:
        raise ValueError("未設定 GOOGLE_EXPORT_COLUMNS，無法匯出資料")

    target = _normalize_target_date(target_date)
    start_of_day = datetime.combine(target, datetime.min.time()).replace(tzinfo=EXPORT_TIMEZONE)
    end_of_day = start_of_day + timedelta(days=1)

    stmt = (
        select(Article)
        .where(
            Article.created_at >= start_of_day,
            Article.created_at < end_of_day,
        )
        .order_by(Article.published_at.desc())
    )
    articles = session.execute(stmt).scalars().all()

    column_resolvers: Dict[str, Callable[[Article], Any]] = {
        "image_url_2": lambda art: "",
    }

    header = [HEADER_LABELS.get(column, column) for column in columns]
    values: List[List[str]] = [header]

    for article in articles:
        row: List[str] = []
        for column in columns:
            resolver = column_resolvers.get(column)
            if resolver:
                value = resolver(article)
            else:
                value = getattr(article, column, None)
            row.append(_format_value(value))
        values.append(row)

    if len(values) == 1:
        logger.info(f"{target} 無文章可匯出，將清空工作表並只保留標題列")

    try:
        credentials = _get_credentials()
        service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
        sheet = service.spreadsheets()

        sheet.values().clear(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range=settings.GOOGLE_SHEET_RANGE,
        ).execute()

        sheet.values().update(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range=settings.GOOGLE_SHEET_RANGE,
            valueInputOption="RAW",
            body={"values": values},
        ).execute()
    except HttpError as exc:
        logger.exception("匯出 Google Sheet 失敗")
        raise RuntimeError(f"Google Sheets API 呼叫失敗: {exc}") from exc

    return len(values) - 1
