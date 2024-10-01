#!/bin/bash

# 다운로드 URL 생성
chrome_url="https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.70/linux64/chrome-headless-shell-linux64.zip"
chromedriver_url="https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.70/linux64/chromedriver-linux64.zip"

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