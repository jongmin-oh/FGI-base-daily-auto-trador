import json
import requests
from datetime import datetime

from app.config import DiscordConfig, TIME_OUT


def send_discord_notification(
    fng_value, fng_type, order, qty, price, usd_krw_rate, cash
):
    """Discord 알림 전송"""

    # 현재 시간
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 임베드 색상 및 제목 설정
    if order == "매도":
        color = 0x0000FF  # 파란색
        title = "트레이딩 봇 알림: 매도 주문 실행"
    elif order == "매수":
        color = 0xFF0000  # 빨간색
        title = "트레이딩 봇 알림: 매수 주문 실행"
    else:  # "매수하지않음"
        color = 0x808080  # 회색
        title = "트레이딩 봇 알림: 매수하지 않음"

    # 메시지 본문 구성
    embed = {
        "title": title,
        "color": color,
        "fields": [
            {
                "name": f"공포 탐욕 지수 {fng_type}",
                "value": str(fng_value),
                "inline": True,
            },
            {"name": "주문 유형", "value": order, "inline": True},
            {"name": "수량", "value": str(qty), "inline": True},
            {"name": "가격 (USD)", "value": f"${price:.2f}", "inline": True},
            {
                "name": "가격 (KRW)",
                "value": f"₩{price * usd_krw_rate:,.0f}",
                "inline": True,
            },
            {"name": "현재 현금 잔고", "value": f"₩{cash:,.0f}", "inline": True},
            {"name": "알림 시각", "value": current_time, "inline": False},
        ],
    }

    # 웹훅 페이로드 구성
    payload = {"embeds": [embed]}

    # 웹훅 전송
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        DiscordConfig.DISCORD_WEBHOOK,
        data=json.dumps(payload),
        headers=headers,
        timeout=TIME_OUT,
    )

    if response.status_code == 204:
        print("Discord 알림이 성공적으로 전송되었습니다.")
    else:
        print(f"Discord 알림 전송 실패. 상태 코드: {response.status_code}")
