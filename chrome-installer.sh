#!/bin/bash

# 다운로드 URL 생성
chrome_url=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chrome[] | select(.platform == "linux64") | .url')
chromedriver_url=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform == "linux64") | .url')

download_path_chrome_linux="/opt/chrome-linux.zip"
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
