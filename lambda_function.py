import time

from app.tasks.trade import AutoTrador
from app.tasks.feerAndGreed import get_fear_greed_index
from app.tasks.discord import send_discord_notification, send_discord_error_alert


def order_stock(trader: AutoTrador) -> dict:
    balance: int = trader.get_balance()  # 현재 현금 잔고
    price: float = trader.get_current_price()  # 1주당 가격 USD

    if balance < (price * trader.usd):  # 환율 적용
        raise ValueError("잔고가 부족합니다.")

    fng_value: int = get_fear_greed_index()

    print(f"Current FNG value: {fng_value}")

    if fng_value <= 25:
        fng_type, qty, behavior = "Extreme Fear", 2, "매수"
        trader.buy(qty, price)
    elif 25 < fng_value < 45:
        fng_type, qty, behavior = "Fear", 1, "매수"
        trader.buy(qty, price)
    elif 45 <= fng_value < 55:
        fng_type, qty, behavior = "Neutral", 0, "행동없음"
    elif 55 <= fng_value < 75:
        fng_type, qty, behavior = "Greed", 1, "매도"
        trader.sell(qty, price)
    elif fng_value >= 75:
        fng_type, qty, behavior = "Extreme Greed", 2, "매도"
        trader.sell(qty, price)
    else:
        raise ValueError("Unexpected FNG value")

    return {
        "fng_value": fng_value,
        "fng_type": fng_type,
        "behavior": behavior,
        "qty": qty,
        "price": price,
    }


def lambda_handler(event, context):
    try:
        trader = AutoTrador()

        while True:  # 주문이 완료될 때까지 반복
            order_result = order_stock(trader)
            time.sleep(3)

            pending_info = trader.check_pending()
            if pending_info["is_pending"] is False:
                break

            trader.cancel_order(
                pdno=pending_info["pdno"],
                qty=pending_info["qty"],
                odno=pending_info["odno"],
            )

        # Discord 알림 전송
        send_discord_notification(
            fng_value=order_result["fng_value"],  # 공포 탐욕 지수
            fng_type=order_result["fng_type"],  # 공포 탐욕 지수 유형
            order=order_result["behavior"],  # 주문 유형
            qty=order_result["qty"],  # 수량
            price=order_result["price"],  # 가격(USD)
            usd_krw_rate=trader.usd,  # 환율
            cash=trader.get_balance(),  # 현재 현금 잔고
        )
    except Exception as e:
        send_discord_error_alert(str(e))
        raise e
