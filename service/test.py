import time
from app.tasks.trade import AutoTrador
from app.tasks.feerAndGreed import get_fear_greed_index
from app.tasks.discord import send_discord_notification

trader = AutoTrador()


def order_stock():
    price: float = trader.get_current_price()  # 1주당 가격 USD
    fng_value = get_fear_greed_index()
    if fng_value <= 25:  # Extreme Fear
        qty = 2
        trader.buy(qty, price)
        behavior = "매수"
    elif fng_value < 45 and fng_value > 25:  # Fear
        qty = 1
        trader.buy(qty, price)
        behavior = "매수"
    elif fng_value < 55 and fng_value >= 45:  # Neutral
        qty = 0
        behavior = "행동없음"
    elif fng_value < 75 and fng_value >= 55:  # Greed
        qty = 1
        trader.sell(qty, price)
        behavior = "매도"
    elif fng_value >= 75:  # Extreme Greed
        qty = 2
        trader.sell(qty, price)
        behavior = "매도"

    return {"fng_value": fng_value, "behavior": behavior, "qty": qty, "price": price}


while True:
    order_result = order_stock()
    time.sleep(3)

    pending_info = trader.check_pending()
    if pending_info["is_pending"] is False:
        break

    trader.cancel_order(
        pdno=pending_info["pdno"],
        qty=pending_info["qty"],
        odno=pending_info["odno"],
    )

send_discord_notification(
    fng_value=order_result["fng_value"],  # 공포 탐욕 지수
    order=order_result["behavior"],  # 주문 유형
    qty=order_result["qty"],  # 수량
    price=order_result["price"],  # 가격(USD)
    usd_krw_rate=trader.usd,  # 환율
    cash=trader.get_balance(),  # 현재 현금 잔고
)
