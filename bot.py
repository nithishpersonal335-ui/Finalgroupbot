import requests
import time
import threading
import pandas as pd
import yfinance as yf
from flask import Flask
from datetime import datetime
import pytz

# ================= CONFIG =================
BOT_TOKEN = "8694926384:AAGE_6UPkci3OcS1_QzPu7Vj5nVoQnBYsvU"
CHAT_ID = "1207682165"

NIFTY = "^NSEI"
BANKNIFTY = "^NSEBANK"

app = Flask(__name__)

# ================= STATE (NO DUPLICATES) =================
last_signal = {
    "NIFTY": None,
    "BANKNIFTY": None
}

# ================= TELEGRAM =================
def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
        print("Sent:", text)
    except Exception as e:
        print("Telegram Error:", e)

# ================= MARKET TIME (IST FIXED) =================
def is_market_open():
    india = pytz.timezone('Asia/Kolkata')
    now = datetime.now(india)

    start = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end = now.replace(hour=15, minute=30, second=0, microsecond=0)

    return start <= now <= end

# ================= DATA =================
def get_data(symbol):
    try:
        data = yf.download(symbol, interval="5m", period="1d")
        if data is None or len(data) < 20:
            return None
        return data
    except Exception as e:
        print("Data Error:", e)
        return None

# ================= SIGNAL =================
def check_signals(name, symbol):
    global last_signal

    data = get_data(symbol)
    if data is None:
        print(f"{name}: No data")
        return

    try:
        data["EMA9"] = data["Close"].ewm(span=9).mean()
        data["EMA15"] = data["Close"].ewm(span=15).mean()

        last = data.iloc[-1]
        prev = data.iloc[-2]

        signal = None

        # BUY crossover
        if prev["EMA9"] < prev["EMA15"] and last["EMA9"] > last["EMA15"]:
            signal = "BUY"

        # SELL crossover
        elif prev["EMA9"] > prev["EMA15"] and last["EMA9"] < last["EMA15"]:
            signal = "SELL"

        # SEND ONLY FRESH SIGNAL
        if signal and last_signal[name] != signal:
            last_signal[name] = signal
            send_message(f"{name} {signal} 📈 EMA 9/15 Crossover")

    except Exception as e:
        print("Signal Error:", e)

# ================= LOOP =================
def run_bot():
    send_message("Bot Started ✅")

    was_open = False

    while True:
        if is_market_open():
            if not was_open:
                print("Market Open Started 🚀")
                was_open = True

            check_signals("NIFTY", NIFTY)
            check_signals("BANKNIFTY", BANKNIFTY)

        else:
            if was_open:
                print("Market Closed ❌")
                was_open = False

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
