name: Daily News Summary
on:
schedule:
- cron: '0 10 * * *' # UTC 기준 10시는 한국 시간 저녁 7시입니다
workflow_dispatch:

jobs:
build:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v3
- name: Set up Python
uses: actions/setup-python@v4
with:
python-version: '3.9'
- name: Install dependencies
run: pip install google-generativeai youtube-transcript-api
- name: Run script
env:
GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
run: python main.py
