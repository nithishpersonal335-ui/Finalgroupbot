import requests
import time
import threading
from flask import Flask

# ================= CONFIG =================
BOT_TOKEN = "8694926384:AAGE_6UPkci3OcS1_QzPu7Vj5nVoQnBYsvU"
CHAT_ID = "1207682165"

app = Flask(__name__)

# ================= TELEGRAM =================
def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
        print("Sent:", text)
    except Exception as e:
        print("Error:", e)

# ================= SIGNAL SYSTEM =================
def check_signals():
    try:
        # 🔹 Dummy rotating signals (to test bot working perfectly)
        current_time = int(time.time()) % 4

        if current_time == 0:
            send_message("NIFTY BUY 📈 EMA Crossover")
        elif current_time == 1:
            send_message("NIFTY SELL 📉 EMA Crossdown")
        elif current_time == 2:
            send_message("BANKNIFTY BUY 🚀 VWAP Breakout")
        elif current_time == 3:
            send_message("BANKNIFTY SELL 🔻 VWAP Breakdown")

    except Exception as e:
        print("Signal Error:", e)

# ================= LOOP =================
def run_bot():
    send_message("Bot Started ✅")
    while True:
        print("Checking signals...")
        check_signals()
        time.sleep(60)  # 1 min

# ================= FLASK =================
@app.route('/')
def home():
    return "Bot is running ✅"

# ================= START =================
if __name__ == "__main__":
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()

    app.run(host="0.0.0.0", port=8080)
