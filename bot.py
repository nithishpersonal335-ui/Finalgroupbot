import requests
import time
import threading
import pandas as pd
import yfinance as yf
from flask import Flask

BOT_TOKEN = "8694926384:AAGE_6UPkci3OcS1_QzPu7Vj5nVoQnBYsvU"
CHAT_ID = "1207682165"

NIFTY = "^NSEI"
BANKNIFTY = "^NSEBANK"

app = Flask(__name__)

# ================= TELEGRAM =================
def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print("Telegram Error:", e)

# ================= SIGNAL =================
def check_signals(name, symbol):
    try:
        data = yf.download(symbol, interval="5m", period="1d")

        if data is None or len(data) < 20:
            print(f"{name}: Not enough data")
            return

        data["EMA9"] = data["Close"].ewm(span=9).mean()
        data["EMA15"] = data["Close"].ewm(span=15).mean()
        data["VWAP"] = (data["Close"] * data["Volume"]).cumsum() / data["Volume"].cumsum()

        last = data.iloc[-1]
        prev = data.iloc[-2]

        # BUY EMA
        if prev["EMA9"] < prev["EMA15"] and last["EMA9"] > last["EMA15"]:
            send_message(f"{name} BUY 📈 EMA Cross")

        # SELL EMA
        elif prev["EMA9"] > prev["EMA15"] and last["EMA9"] < last["EMA15"]:
            send_message(f"{name} SELL 📉 EMA Cross")

        # VWAP BUY
        elif prev["Close"] < prev["VWAP"] and last["Close"] > last["VWAP"]:
            send_message(f"{name} BUY 🚀 VWAP Break")

        # VWAP SELL
        elif prev["Close"] > prev["VWAP"] and last["Close"] < last["VWAP"]:
            send_message(f"{name} SELL 🔻 VWAP Break")

    except Exception as e:
        print("Signal Error:", e)

# ================= LOOP =================
def run_bot():
    send_message("Bot Started ✅")
    while True:
        print("Checking signals...")
        check_signals("NIFTY", NIFTY)
        check_signals("BANKNIFTY", BANKNIFTY)
        time.sleep(60)

# ================= ROUTE =================
@app.route('/')
def home():
    return "Bot is running"

# ================= START =================
if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=8080)
