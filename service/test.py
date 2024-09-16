from app.tasks.trade import AutoTrador

if __name__ == "__main__":
    trader = AutoTrador()
    price = trader.get_current_price()
    print(int(price * trader.usd), "원")

    cash = trader.get_balance()
    print(f"주문 가능 현금 잔고: {cash}원")
