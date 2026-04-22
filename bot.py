import os
import requests
import threading
import time
from flask import Flask

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ================= TELEGRAM FUNCTION =================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, data=data)
        print("Message sent:", response.text)
    except Exception as e:
        print("Error sending message:", e)

# ================= TEST MESSAGE =================
def test_message():
    send_message("Test message ✅ Bot is working")

# ================= SELF PING =================
def self_ping():
    while True:
        try:
            requests.get("https://finalgroupbot-production.up.railway.app")
            print("Self ping success")
        except:
            print("Self ping failed")
        time.sleep(300)

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running ✅"

# ================= MAIN =================
if __name__ == "__main__":
    print("Bot Started...")

    test_message()

    threading.Thread(target=self_ping).start()

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
