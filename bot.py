import requests
import time
import threading
from flask import Flask

BOT_TOKEN = "8285229070:AAGZQnCbjULqMUsZkmNMBSG9NCh3WlI2bNo"
CHAT_ID = "1207682165"

APP_URL = "https://simplebot-production-11a0.up.railway.app"

# ===== TELEGRAM =====
def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# ===== EMA SERIES (FIXED) =====
def ema_series(prices, period):
    k = 2 / (period + 1)
    ema_vals = [prices[0]]
    for p in prices[1:]:
        ema_vals.append(p * k + ema_vals[-1] * (1 - k))
    return ema_vals

# ===== VWAP =====
def vwap(prices, volumes):
    total_pv = sum(p * v for p, v in zip(prices, volumes))
    total_v = sum(volumes)
    return total_pv / total_v if total_v else None

# ===== FETCH DATA =====
def get_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return [], []

        data = r.json()

        if not data.get("chart") or not data["chart"].get("result"):
            return [], []

        result = data["chart"]["result"][0]

        closes = result["indicators"]["quote"][0]["close"]
        volumes = result["indicators"]["quote"][0]["volume"]

        closes = [c for c in closes if c]
        volumes = [v for v in volumes if v]

        return closes, volumes

    except Exception as e:
        print("Data error:", e)
        return [], []

# ===== MEMORY =====
last_fast = {}
last_confirmed = {}
last_target = {}
last_orb = {}

# ===== MAIN LOGIC =====
def check(symbol, name):
    global last_fast, last_confirmed, last_target, last_orb

    prices, volumes = get_data(symbol)

    if len(prices) < 15:
        print(name, "waiting for data...")
        return

    # EMA SERIES (FULL DAY WORKING)
    ema9 = ema_series(prices, 9)
    ema15 = ema_series(prices, 15)

    if len(ema9) < 2 or len(ema15) < 2:
        return

    ema9_prev = ema9[-2]
    ema15_prev = ema15[-2]

    ema9_now = ema9[-1]
    ema15_now = ema15[-1]

    current_price = prices[-1]
    prev_price = prices[-2]

    current_vwap = vwap(prices, volumes)

    # ===== 1. EMA CROSS =====
    if ema9_prev < ema15_prev and ema9_now > ema15_now:
        if last_fast.get(name) != "BUY":
            send_msg(f"{name} EMA BUY ⚡")
            last_fast[name] = "BUY"

    elif ema9_prev > ema15_prev and ema9_now < ema15_now:
        if last_fast.get(name) != "SELL":
            send_msg(f"{name} EMA SELL ⚡")
            last_fast[name] = "SELL"

    # ===== 2. CONFIRMED =====
    if current_vwap:
        if ema9_prev < ema15_prev and ema9_now > ema15_now and current_price > current_vwap:
            if last_confirmed.get(name) != "BUY":
                send_msg(f"{name} BUY 🔼 (Confirmed)")
                last_confirmed[name] = "BUY"

        elif ema9_prev > ema15_prev and ema9_now < ema15_now and current_price < current_vwap:
            if last_confirmed.get(name) != "SELL":
                send_msg(f"{name} SELL 🔽 (Confirmed)")
                last_confirmed[name] = "SELL"

    # ===== 3. TARGET (40pt) =====
    if current_vwap:
        bullish = current_price - prev_price > 0.2 * current_price / 100
        bearish = prev_price - current_price > 0.2 * current_price / 100

        if ema9_now > ema15_now and current_price > current_vwap and bullish:
            if last_target.get(name) != "BUY":
                send_msg(f"{name} TARGET BUY 🎯")
                last_target[name] = "BUY"

        elif ema9_now < ema15_now and current_price < current_vwap and bearish:
            if last_target.get(name) != "SELL":
                send_msg(f"{name} TARGET SELL 🎯")
                last_target[name] = "SELL"

    # ===== 4. ORB =====
    if len(prices) >= 3:
        orb_high = max(prices[:3])
        orb_low = min(prices[:3])

        if current_vwap:
            if current_price > orb_high and current_price > current_vwap:
                if last_orb.get(name) != "BUY":
                    send_msg(f"{name} ORB BUY 🚀")
                    last_orb[name] = "BUY"

            elif current_price < orb_low and current_price < current_vwap:
                if last_orb.get(name) != "SELL":
                    send_msg(f"{name} ORB SELL 🔻")
                    last_orb[name] = "SELL"

# ===== BOT LOOP =====
def run_bot():
    send_msg("Bot started (Final Version ✅)")

    while True:
        try:
            check("^NSEI", "NIFTY")
            check("^NSEBANK", "BANKNIFTY")

            # self ping (keep alive)
            try:
                requests.get(APP_URL, timeout=5)
            except:
                pass

            time.sleep(300)

        except Exception as e:
            print("Main error:", e)
            time.sleep(60)

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running"

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
