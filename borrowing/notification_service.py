import os

import requests
from dotenv import load_dotenv


def send_message(msg):
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = f"?chat_id={chat_id}&text={msg}"
    response = requests.get(url + params)
    return response
