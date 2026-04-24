import requests
import time
import threading
import pandas as pd
import yfinance as yf
from flask import Flask

# ================== CONFIG ==================
BOT_TOKEN = "8694926384:AAGE_6UPkci3OcS1_QzPu7Vj5nVoQnBYsvU"
CHAT_ID = "1207682165"

# Symbols
NIFTY = "^NSEI"
BANKNIFTY = "^NSEBANK"

# ================== TELEGRAM ==================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        res = requests.post(url, data=data)
        print("Message:", res.text)
    except Exception as e:
        print("Error:", e)

# ================== SIGNAL LOGIC ==================
def check_signals(name, symbol):
    try:
        data = yf.download(symbol, interval="5m", period="1d")

        if data.empty:
            return

        # Indicators
        data["EMA9"] = data["Close"].ewm(span=9).mean()
        data["EMA15"] = data["Close"].ewm(span=15).mean()
        data["VWAP"] = (data["Close"] * data["Volume"]).cumsum() / data["Volume"].cumsum()

        last = data.iloc[-1]
        prev = data.iloc[-2]

        # ================== 4 SIGNALS ==================
        
        # 1. EMA Crossover BUY
        if prev["EMA9"] < prev["EMA15"] and last["EMA9"] > last["EMA15"]:
            send_message(f"{name} BUY 📈 EMA 9/15 Crossover")

        # 2. EMA Crossover SELL
        elif prev["EMA9"] > prev["EMA15"] and last["EMA9"] < last["EMA15"]:
            send_message(f"{name} SELL 📉 EMA 9/15 Crossdown")

        # 3. VWAP Breakout BUY
        elif last["Close"] > last["VWAP"] and prev["Close"] < prev["VWAP"]:
            send_message(f"{name} BUY 🚀 VWAP Breakout")

        # 4. VWAP Breakdown SELL
        elif last["Close"] < last["VWAP"] and prev["Close"] > prev["VWAP"]:
            send_message(f"{name} SELL 🔻 VWAP Breakdown")

    except Exception as e:
        print("Signal Error:", e)

# ================== BOT LOOP ==================
def run_bot():
    send_message("Bot Started ✅")
    while True:
        print("Checking signals...")
        check_signals("NIFTY", NIFTY)
        check_signals("BANKNIFTY", BANKNIFTY)
        time.sleep(60)  # 1 minute delay

# ================== FLASK SERVER ==================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

# ================== MAIN ==================
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
