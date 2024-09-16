import json
import datetime
from pytz import timezone

import requests

from app.config import Config


class TradeManager:

    @staticmethod
    def get_access_token():
        """토큰 발급"""
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": Config.API_KEY,
            "appsecret": Config.SECRET_KEY,
        }
        PATH = "oauth2/tokenP"
        URL = f"{Config.HOST}/{PATH}"
        res = requests.post(URL, headers=headers, data=json.dumps(body), timeout=5)
        ACCESS_TOKEN = res.json()["access_token"]
        return ACCESS_TOKEN

    @staticmethod
    def hashkey(datas):
        """암호화"""
        PATH = "uapi/hashkey"
        URL = f"{Config.HOST}/{PATH}"
        headers = {
            "content-Type": "application/json",
            "appKey": Config.API_KEY,
            "appSecret": Config.SECRET_KEY,
        }
        res = requests.post(URL, headers=headers, data=json.dumps(datas), timeout=5)
        hashkey = res.json()["HASH"]
        return hashkey


class AutoTrador:
    def __init__(self):
        self.market = "AMEX"
        self.code = "SPYG"
