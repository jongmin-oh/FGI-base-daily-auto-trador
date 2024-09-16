import requests

from app.config import DiscordConfig, TIME_OUT


def send_alert(title: str, message: str):
    payload = {
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": 5814783,  # 색상은 선택사항입니다. 이 예제에서는 밝은 파란색을 사용합니다.
            }
        ]
    }
    response = requests.post(
        DiscordConfig.DISCORD_WEBHOOK,
        json=payload,
        timeout=TIME_OUT,
    )
    response.raise_for_status()
