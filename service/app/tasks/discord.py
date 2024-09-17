import json
import requests

from app.config import DiscordConfig, TIME_OUT


def send_discord_notification(fng_value, order, qty, price, usd_krw_rate, cash):
    # 임베드 색상 및 제목 설정
    if order == "매수":
        color = 0x00FF00  # 초록색
        title = "트레이딩 봇 알림: 매수 주문 실행"
    elif order == "매도":
        color = 0xFF0000  # 빨간색
        title = "트레이딩 봇 알림: 매도 주문 실행"
    else:  # "매수하지않음"
        color = 0xFFFF00  # 노란색
        title = "트레이딩 봇 알림: 매수하지 않음"

    # 메시지 본문 구성
    embed = {
        "title": title,
        "color": color,
        "fields": [
            {"name": "공포 탐욕 지수", "value": str(fng_value), "inline": True},
            {"name": "주문 유형", "value": order, "inline": True},
            {"name": "수량", "value": str(qty), "inline": True},
            {"name": "가격 (USD)", "value": f"${price:.2f}", "inline": True},
            {
                "name": "가격 (KRW)",
                "value": f"₩{price * usd_krw_rate:,.0f}",
                "inline": True,
            },
            {"name": "현재 현금 잔고", "value": f"${cash:.2f}", "inline": True},
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
