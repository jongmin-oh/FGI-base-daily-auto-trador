import json
from datetime import datetime
from pytz import timezone
import requests

from app.config import Config, Paths, TIME_OUT

seoul_tz = timezone("Asia/Seoul")


class TradeManager:
    @staticmethod
    def is_token_expired(token_data: dict) -> bool:
        expiry_time = datetime.strptime(
            token_data["access_token_token_expired"], "%Y-%m-%d %H:%M:%S"
        )
        expiry_time = seoul_tz.localize(expiry_time)
        current_time = datetime.now(seoul_tz)

        return current_time > expiry_time

    @staticmethod
    def get_access_token():
        """토큰 발급"""
        # 이전에 발급받은 토큰이 존재하고, 만료기간이 남아있는 경우
        if Paths.ACCESS_TOKEN_PATH.exists():
            prev_token = json.loads(
                open(Paths.ACCESS_TOKEN_PATH, "r", encoding="utf-8").read()
            )
            if not TradeManager.is_token_expired(prev_token):
                return prev_token["access_token"]

        # 토큰이 존재하지 않거나 만료된 경우
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": Config.API_KEY,
            "appsecret": Config.SECRET_KEY,
        }
        PATH = "oauth2/tokenP"
        URL = f"{Config.HOST}/{PATH}"
        res = requests.post(
            URL, headers=headers, data=json.dumps(body), timeout=TIME_OUT
        )

        with open(Paths.ACCESS_TOKEN_PATH, "w", encoding="utf-8") as f:
            json.dump(res.json(), f, ensure_ascii=False, indent=4)

        return res.json()["access_token"]

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
        res = requests.post(
            URL, headers=headers, data=json.dumps(datas), timeout=TIME_OUT
        )
        hashkey = res.json()["HASH"]
        return hashkey

    @staticmethod
    def get_exchange_rate():
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        # API에 요청 보내기
        response = requests.get(url, timeout=TIME_OUT)
        data = response.json()

        # 요청이 성공했는지 확인
        if response.status_code == 200:
            # 목표 통화의 환율 반환
            return data["rates"]["KRW"]
        else:
            print("API 요청 실패:", data["error"])
            return None


class AutoTrador:
    def __init__(self):
        self.market = "AMS"
        self.code = "SPYG"
        self.access_token = TradeManager.get_access_token()
        self.usd = TradeManager.get_exchange_rate()

    def get_current_price(self):
        """현재가 조회"""
        PATH = "uapi/overseas-price/v1/quotations/price"
        URL = f"{Config.HOST}/{PATH}"
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appKey": Config.API_KEY,
            "appSecret": Config.SECRET_KEY,
            "tr_id": "HHDFS00000300",
        }
        params = {
            "AUTH": "",
            "EXCD": self.market,
            "SYMB": self.code,
        }
        res = requests.get(URL, headers=headers, params=params, timeout=TIME_OUT)
        return float(res.json()["output"]["last"])

    def get_balance(self):
        """현금 잔고조회"""
        PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"
        URL = f"{Config.HOST}/{PATH}"
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appKey": Config.API_KEY,
            "appSecret": Config.SECRET_KEY,
            "tr_id": "TTTC8908R",
            "custtype": "P",
        }
        params = {
            "CANO": Config.CANO,
            "ACNT_PRDT_CD": Config.ACNT_PRDT_CD,
            "PDNO": "005930",
            "ORD_UNPR": "65500",
            "ORD_DVSN": "01",
            "CMA_EVLU_AMT_ICLD_YN": "Y",
            "OVRS_ICLD_YN": "Y",
        }
        res = requests.get(URL, headers=headers, params=params, timeout=TIME_OUT)
        cash = res.json()["output"]["ord_psbl_cash"]

        return int(cash)
