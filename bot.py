import requests
import time
import threading
import pandas as pd
import yfinance as yf
from flask import Flask

# ================= CONFIG =================
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
        print("Sent:", text)
    except Exception as e:
        print("Telegram Error:", e)

# ================= SIGNAL =================
def get_data(symbol):
    try:
        data = yf.download(symbol, interval="5m", period="1d")
        if data is None or len(data) < 20:
            return None
        return data
    except:
        return None

def check_signals(name, symbol):
    data = get_data(symbol)

    if data is None:
        print(f"{name}: No data")
        return

    try:
        data["EMA9"] = data["Close"].ewm(span=9).mean()
        data["EMA15"] = data["Close"].ewm(span=15).mean()
        data["VWAP"] = (data["Close"] * data["Volume"]).cumsum() / data["Volume"].cumsum()

        last = data.iloc[-1]
        prev = data.iloc[-2]

        # 1️⃣ EMA Crossover
        if prev["EMA9"] < prev["EMA15"] and last["EMA9"] > last["EMA15"]:
            send_message(f"{name} BUY 📈 EMA Crossover")

        elif prev["EMA9"] > prev["EMA15"] and last["EMA9"] < last["EMA15"]:
            send_message(f"{name} SELL 📉 EMA Crossdown")

        # 2️⃣ Confirmed (EMA + VWAP)
        elif last["EMA9"] > last["EMA15"] and last["Close"] > last["VWAP"]:
            send_message(f"{name} STRONG BUY ✅ (EMA + VWAP)")

        elif last["EMA9"] < last["EMA15"] and last["Close"] < last["VWAP"]:
            send_message(f"{name} STRONG SELL ❌ (EMA + VWAP)")

        # 3️⃣ 40 Points Momentum (simple logic)
        elif abs(last["Close"] - prev["Close"]) > 40:
            send_message(f"{name} ⚡ Momentum Move (40 pts)")

        # 4️⃣ ORB (Opening Range Breakout)
        elif last["High"] > data["High"].iloc[:5].max():
            send_message(f"{name} 🚀 ORB Breakout")

        elif last["Low"] < data["Low"].iloc[:5].min():
            send_message(f"{name} 🔻 ORB Breakdown")

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
