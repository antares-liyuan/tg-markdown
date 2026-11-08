"""Send a Markdown message to Telegram with HTML rendering and a plain-text fallback.
Usage: TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... python3 example_send.py
"""
import json, os, urllib.error, urllib.parse, urllib.request
import tg_markdown

TOKEN, CHAT = os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]
API = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


def post(fields):
    req = urllib.request.Request(API, data=urllib.parse.urlencode(fields).encode())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def send_markdown(text):
    for part in tg_markdown.split_html_safe(text, 3800):
        try:
            post({"chat_id": CHAT, "text": tg_markdown.to_html(part), "parse_mode": "HTML", "disable_web_page_preview": "true"})
        except urllib.error.HTTPError as e:
            if e.code != 400:
                raise
            post({"chat_id": CHAT, "text": tg_markdown.to_plain(part)})      # HTML rejected: send plain text instead


if __name__ == "__main__":
    send_markdown("""# Report
**Status**: all good
| item | result |
|---|---|
| tests | ✅ 6 passed |
- see [docs](https://core.telegram.org/bots/api#html-style)""")
