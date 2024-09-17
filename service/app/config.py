from typing import Final
from pathlib import Path
from dataclasses import dataclass

import yaml

CRAWL_URL: Final[str] = "https://edition.cnn.com/markets/fear-and-greed"
TIME_OUT: Final[int] = 10


@dataclass(frozen=True)
class Paths:
    BASE_DIR: Path = Path(__file__).resolve().parent
    SECRETS_PATH: Path = BASE_DIR.joinpath("secrets.yml")
    ACCESS_TOKEN_PATH: Path = BASE_DIR.joinpath("access_token.json")


with open(Paths.SECRETS_PATH, "r", encoding="utf-8") as file:
    SECRETS = yaml.safe_load(file)


@dataclass(frozen=True)
class Config:
    API_KEY = SECRETS["KOREA_INVESTMENT"]["API_KEY"]
    SECRET_KEY = SECRETS["KOREA_INVESTMENT"]["SECRET_KEY"]
    HOST = SECRETS["KOREA_INVESTMENT"]["HOST"]
    CANO = SECRETS["KOREA_INVESTMENT"]["CANO"]
    ACNT_PRDT_CD = SECRETS["KOREA_INVESTMENT"]["ACNT_PRDT_CD"]
    PHONE_NUMBER = SECRETS["PHONE_NUMBER"]


@dataclass(frozen=True)
class DiscordConfig:
    DISCORD_WEBHOOK = SECRETS["DISCORD"]["WEBHOOK_URL"]
