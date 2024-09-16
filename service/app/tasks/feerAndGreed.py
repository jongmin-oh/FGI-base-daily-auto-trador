import requests
from bs4 import BeautifulSoup

from app.config import CRAWL_URL


def get_fear_greed_index() -> float:
    response = requests.get(CRAWL_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # 'text-end fw-bold text-sm' 클래스를 가진 td 태그를 찾습니다.
    value_td = soup.find("td", class_="text-end fw-bold text-sm")

    if value_td:
        # td 태그 내의 텍스트를 가져와 공백을 제거합니다.
        value = value_td.text.strip()
        return float(value)
    else:
        raise ValueError("Failed to find the FNG index value.")
