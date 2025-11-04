import os
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sportsnavi API"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # Selenium 設定
    SELENIUM_HOST: str = "selenium"
    SELENIUM_PORT: int = 4444

    # Yahoo Sports 新聞來源設定
    NEWS_SOURCES: Dict[str, Dict[str, Any]] = {
        # 棒球
        "npb": {
            "name": "日本職棒 NPB",
            "base_url": "https://baseball.yahoo.co.jp/npb/"
        },
        "mlb": {
            "name": "美國大聯盟 MLB",
            "base_url": "https://baseball.yahoo.co.jp/mlb/"
        },
        "hsb": {
            "name": "高校野球",
            "base_url": "https://baseball.yahoo.co.jp/hsb/"
        },
        "bbl": {
            "name": "大學野球",
            "base_url": "https://baseball.yahoo.co.jp/bbl/"
        },
        "amateur": {
            "name": "業餘棒球",
            "base_url": "https://baseball.yahoo.co.jp/amateur/"
        },
        "ipbl": {
            "name": "独立リーグ",
            "base_url": "https://baseball.yahoo.co.jp/ipbl/"
        },
        "baseball_japan": {
            "name": "侍ジャパン",
            "base_url": "https://baseball.yahoo.co.jp/japan/"
        },
        # 足球
        "jleague": {
            "name": "Jリーグ",
            "base_url": "https://soccer.yahoo.co.jp/jleague/"
        },
        "ws": {
            "name": "海外サッカー",
            "base_url": "https://soccer.yahoo.co.jp/ws/"
        },
        "soccer_japan": {
            "name": "サッカー代表",
            "base_url": "https://soccer.yahoo.co.jp/japan/"
        },
        "youth_soccer": {
            "name": "高校年代",
            "base_url": "https://soccer.yahoo.co.jp/youth/"
        },
        # 其他運動
        "keiba": {
            "name": "競馬",
            "base_url": "https://sports.yahoo.co.jp/keiba/"
        },
        "boatrace": {
            "name": "ボートレース",
            "base_url": "https://sports.yahoo.co.jp/boatrace/"
        },
        "sumo": {
            "name": "大相撲",
            "base_url": "https://sports.yahoo.co.jp/sumo/"
        },
        "figureskate": {
            "name": "フィギュア",
            "base_url": "https://sports.yahoo.co.jp/figureskate/"
        },
        "curling": {
            "name": "カーリング",
            "base_url": "https://sports.yahoo.co.jp/curling/"
        },
        "fight": {
            "name": "格闘技",
            "base_url": "https://sports.yahoo.co.jp/fight/"
        },
        "golf": {
            "name": "ゴルフ",
            "base_url": "https://sports.yahoo.co.jp/golf/"
        },
        "tennis": {
            "name": "テニス",
            "base_url": "https://sports.yahoo.co.jp/tennis/"
        },
        "tabletennis": {
            "name": "卓球",
            "base_url": "https://sports.yahoo.co.jp/tabletennis/"
        },
        "badminton": {
            "name": "バドミントン",
            "base_url": "https://sports.yahoo.co.jp/badminton/"
        },
        "f1": {
            "name": "F1",
            "base_url": "https://sports.yahoo.co.jp/f1/"
        },
        "volley": {
            "name": "バレーボール",
            "base_url": "https://sports.yahoo.co.jp/volley/"
        },
        "rugby": {
            "name": "ラグビー",
            "base_url": "https://sports.yahoo.co.jp/rugby/"
        },
        "athletic": {
            "name": "陸上",
            "base_url": "https://sports.yahoo.co.jp/athletic/"
        },
        "bleague": {
            "name": "Bリーグ",
            "base_url": "https://sports.yahoo.co.jp/basket/bleague/"
        },
        "nba": {
            "name": "NBA",
            "base_url": "https://sports.yahoo.co.jp/basket/nba/"
        },
        "basket_japan": {
            "name": "バスケ代表",
            "base_url": "https://sports.yahoo.co.jp/basket/japan/"
        },
        "youth_basket": {
            "name": "学生バスケ",
            "base_url": "https://sports.yahoo.co.jp/basket/youth/"
        },
        "other": {
            "name": "他競技",
            "base_url": "https://sports.yahoo.co.jp/other/"
        },
        "dosports": {
            "name": "Doスポーツ",
            "base_url": "https://sports.yahoo.co.jp/dosports/"
        }
    }

    # 資料庫設定
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "db"
    POSTGRES_DB: str = "sportsnavidb"
    DATABASE_URL: Optional[str] = None

    # Chrome 設定
    CHROME_BIN: str = "/usr/bin/chromium"
    CHROMEDRIVER_PATH: str = "/usr/bin/chromedriver"
    CHROME_HEADLESS: bool = True
    DISABLE_IMAGES: bool = True

    # 爬蟲設定
    CRAWLER_MAX_RETRIES: int = 3
    CRAWLER_TIMEOUT: int = 30
    CRAWLER_DELAY_MIN: int = 1
    CRAWLER_DELAY_MAX: int = 3

    # 記憶體管理設定
    MAX_CONCURRENT_CRAWLERS: int = int(os.getenv('MAX_CONCURRENT_CRAWLERS', '3'))
    MAX_RAM_GB: int = 8
    RESERVED_RAM_GB: int = 2

    # 資料保留設定
    RETENTION_MONTHS: int = 13

    # 日誌設定
    LOG_LEVEL: str = "INFO"

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return (
            f"postgresql://"
            f"{values.get('POSTGRES_USER')}:"
            f"{values.get('POSTGRES_PASSWORD')}@"
            f"{values.get('POSTGRES_SERVER')}/"
            f"{values.get('POSTGRES_DB')}"
        )

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if v == "your-secret-key" or v == "your-secret-key-change-this-in-production":
            raise ValueError("Please change SECRET_KEY in production environment")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
