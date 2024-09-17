from typing import Union, Dict

import json
from datetime import datetime
from pytz import timezone
import requests

from app.config import Config, Paths, TIME_OUT
from app.utility.utils import round_up_to_second_decimal, truncate_to_second_decimal

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
        self.excd = "AMS"
        self.market = "AMEX"
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
            "EXCD": self.excd,
            "SYMB": self.code,
        }
        res = requests.get(URL, headers=headers, params=params, timeout=TIME_OUT)
        return float(res.json()["output"]["last"])

    def get_balance(self) -> int:
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

    def buy(self, qty: int, price: float) -> bool:
        """미국 주식 지정가 매수"""

        price = round_up_to_second_decimal(price)  # 소수점 2자리까지 반올림

        PATH = "uapi/overseas-stock/v1/trading/order"
        URL = f"{Config.HOST}/{PATH}"
        data = {
            "CANO": Config.CANO,  # 종합계좌번호
            "ACNT_PRDT_CD": Config.ACNT_PRDT_CD,  # 계좌상품코드
            "OVRS_EXCG_CD": self.market,  # 해외거래소코드
            "PDNO": self.code,  # 종목코드
            "ORD_DVSN": "00",  # 00 : 지정가
            "ORD_QTY": str(int(qty)),  # 주문수량
            "OVRS_ORD_UNPR": f"{round(price,2)}",
            "ORD_SVR_DVSN_CD": "0",  # 주문서버구분코드
        }
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appKey": Config.API_KEY,
            "appSecret": Config.SECRET_KEY,
            "tr_id": "TTTT1002U",  # TTTT1002U : 미국 매수 주문
            "custtype": "P",  # P : 개인
            "hashkey": TradeManager.hashkey(data),
        }
        res = requests.post(
            URL, headers=headers, data=json.dumps(data), timeout=TIME_OUT
        )

        response = res.json()

        if response["rt_cd"] == "0":
            print(f"[매수 성공] : {response}")
            return True
        else:
            print(f"[매수 실패] : {response}")
            return False

    def sell(self, qty: int, price: float) -> bool:
        """미국 주식 지정가 매도"""

        price = truncate_to_second_decimal(price)  # 소수점 2자리까지 버림
        PATH = "uapi/overseas-stock/v1/trading/order"
        URL = f"{Config.HOST}/{PATH}"
        data = {
            "CANO": Config.CANO,
            "ACNT_PRDT_CD": Config.ACNT_PRDT_CD,
            "OVRS_EXCG_CD": self.market,
            "PDNO": self.code,
            "ORD_DVSN": "00",
            "ORD_QTY": str(int(qty)),
            "OVRS_ORD_UNPR": f"{round(price,2)}",
            "ORD_SVR_DVSN_CD": "0",
        }
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appKey": Config.API_KEY,
            "appSecret": Config.SECRET_KEY,
            "tr_id": "TTTT1006U",
            "custtype": "P",
            "hashkey": TradeManager.hashkey(data),
        }
        res = requests.post(
            URL, headers=headers, data=json.dumps(data), timeout=TIME_OUT
        )
        response = res.json()

        if response["rt_cd"] == "0":
            print(f"[매도 성공] : {response['msg1']}")
            return True
        else:
            print(f"[매도 실패] : {response['msg1']}")
            return False

    def check_pending(self) -> dict:
        """미체결 확인"""
        PATH = "uapi/overseas-stock/v1/trading/inquire-nccs"
        URL = f"{Config.HOST}/{PATH}"

        params = {
            "CANO": Config.CANO,
            "ACNT_PRDT_CD": Config.ACNT_PRDT_CD,
            "OVRS_EXCG_CD": self.market,
            "SORT_SQN": "DS",
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }

        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appKey": Config.API_KEY,
            "appSecret": Config.SECRET_KEY,
            "tr_id": "TTTS3018R",
            "custtype": "P",
        }

        res = requests.post(URL, headers=headers, params=params, timeout=TIME_OUT)
        response = res.json()

        if len(response["output"]) == 0:
            return {"is_pending": False}
        else:
            return {
                "is_pending": True,
                "pdno": response["output"][0]["pdno"],
                "odno": response["output"][0]["odno"],
                "qty": response["output"][0]["ft_ord_qty"],
            }

    def cancel_order(self, qty: str, pdno: str, odno: str) -> bool:
        """미체결 취소"""
        PATH = "uapi/overseas-stock/v1/trading/order-rvsecncl"
        URL = f"{Config.HOST}/{PATH}"
        data = {
            "CANO": Config.CANO,
            "ACNT_PRDT_CD": Config.ACNT_PRDT_CD,
            "OVRS_EXCG_CD": self.market,
            "PDNO": pdno,
            "ORGN_ODNO": odno,
            "RVSE_CNCL_DVSN_CD": "02",  # 02 : 취소
            "ORD_QTY": qty,
            "OVRS_ORD_UNPR": "0",  # 최소주문 시 "0" 입력
        }
        headers = {
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.access_token}",
            "appKey": Config.API_KEY,
            "appSecret": Config.SECRET_KEY,
            "tr_id": "TTTT1004U",
            "custtype": "P",
            "hashkey": TradeManager.hashkey(data),
        }
        res = requests.post(
            URL, headers=headers, data=json.dumps(data), timeout=TIME_OUT
        )
        response = res.json()

        if response["rt_cd"] == "0":
            print(f"[취소 성공] : {response['msg1']}")
            return {"status": 200, "msg": response["msg1"]}
        else:
            print(f"[취소 실패] : {response['msg1']}")
            return {"status": 500, "msg": response["msg1"]}
