import requests

def load_credentials():
    with open("cred.txt") as f:
        lines = f.read().splitlines()
        creds = dict(line.replace('"','').split(" = ") for line in lines)
    return creds["BOT_TOKEN"], creds["CHAT_ID"]

def send_telegram_message(message):
    token, chat_id = load_credentials()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        print("Status:", response.status_code)
        print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print("❌ Telegram request failed:", e)
