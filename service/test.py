from app.tasks.trade import AutoTrador

if __name__ == "__main__":
    trader = AutoTrador()
    price: float = trader.get_current_price()  # 1주당 가격 USD
    won = int(price * trader.usd)  # 1주당 가격 KRW

    print(price)

    cash: int = trader.get_balance()
    print(f"주문 가능 현금 잔고: {cash}원")

    qty = 1
    if cash >= won * qty:
        trader.buy(qty, price)
    else:
        print("주문 가능 현금 잔고 부족")

    trader.sell(qty, price)
