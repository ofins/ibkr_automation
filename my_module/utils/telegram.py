import time

import requests

TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    json = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    response = requests.post(url, json=json)
    return response.json()


def get_telegram_response():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    last_update_id = None
    start_time = time.time()

    while time.time() - start_time < 30:
        response = requests.get(url).json()
        updates = response.get("result", [])

        for update in updates:
            update_id = update.get("update_id")
            message_text = update.get("message", {}).get("text").strip().lower()

            if (
                update_id
                and message_text
                and (last_update_id is None or update_id > last_update_id)
            ):
                last_update_id = update_id
                return message_text

        time.sleep(3)

    return "no"
