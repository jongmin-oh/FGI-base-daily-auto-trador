#!/bin/bash
# Chrome 브라우저 최신 안정 버전 확인
chrome_version=$(curl -s https://omahaproxy.appspot.com/all.json | jq -r '.[] | select(.os=="linux") | .versions[] | select(.channel=="stable") | .current_version')

# ChromeDriver 최신 안정 버전 확인
chromedriver_version=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)

# 운영 체제 확인
os="linux64"
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [[ $(uname -m) == "arm64" ]]; then
        os="mac_arm64"
    else
        os="mac64"
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    os="win32"
fi

# 다운로드 URL 생성
chrome_url="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
if [[ "$os" == "mac64" || "$os" == "mac_arm64" ]]; then
    chrome_url="https://dl.google.com/chrome/mac/stable/GGRO/googlechrome.dmg"
elif [[ "$os" == "win32" ]]; then
    chrome_url="https://dl.google.com/chrome/install/ChromeStandaloneSetup64.exe"
fi

chromedriver_url="https://chromedriver.storage.googleapis.com/${chromedriver_version}/chromedriver_${os}.zip"

download_path_chrome_linux="/opt/chrome-headless-shell-linux.zip"
download_path_chrome_driver_linux="/opt/chromedriver-linux.zip"

mkdir -p "/opt/chrome"
curl -Lo $download_path_chrome_linux $chrome_url
unzip -q $download_path_chrome_linux -d /opt/chrome
rm -rf $download_path_chrome_linux

mkdir -p "/opt/chromedriver"
curl -Lo $download_path_chrome_driver_linux $chromedriver_url
unzip -q $download_path_chrome_driver_linux -d /opt/chromedriver
rm -rf $download_path_chrome_driver_linux

echo "Chrome and ChromeDriver installed successfully."
