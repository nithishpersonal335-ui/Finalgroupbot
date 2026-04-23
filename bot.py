import requests
import time
import pandas as pd
import yfinance as yf

# ===== CONFIG =====
BOT_TOKEN = "8694926384:AAGE_6UPkci3OcS1_QzPu7Vj5nVoQnBYsvU"
CHAT_ID = "1207682165"

# Symbols
NIFTY = "^NSEI"
BANKNIFTY = "^NSEBANK"

# ===== TELEGRAM FUNCTION =====
def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    try:
        res = requests.post(url, data=data)
        print(res.text)
    except Exception as e:
        print("Error:", e)

# ===== FETCH DATA =====
def get_data(symbol):
    df = yf.download(symbol, interval="5m", period="1d")
    return df

# ===== EMA CALCULATION =====
def calculate_ema(df):
    df['EMA9'] = df['Close'].ewm(span=9).mean()
    df['EMA15'] = df['Close'].ewm(span=15).mean()
    return df

# ===== SIGNAL LOGIC =====
def check_signals(symbol_name, symbol):

    df = get_data(symbol)

    if df is None or len(df) < 20:
        print("Not enough data")
        return

    df = calculate_ema(df)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    price = last['Close']

    # ===== 1️⃣ EMA CROSSOVER =====
    if prev['EMA9'] < prev['EMA15'] and last['EMA9'] > last['EMA15']:
        send_message(f"📊 {symbol_name} BUY EMA CROSSOVER @ {price}")

    elif prev['EMA9'] > prev['EMA15'] and last['EMA9'] < last['EMA15']:
        send_message(f"📊 {symbol_name} SELL EMA CROSSOVER @ {price}")

    # ===== 2️⃣ CONFIRMED SIGNAL =====
    if last['EMA9'] > last['EMA15'] and price > last['EMA9']:
        send_message(f"✅ {symbol_name} CONFIRMED BUY @ {price}")

    elif last['EMA9'] < last['EMA15'] and price < last['EMA9']:
        send_message(f"✅ {symbol_name} CONFIRMED SELL @ {price}")

    # ===== 3️⃣ 40 POINT TARGET SYSTEM =====
    if last['EMA9'] > last['EMA15']:
        target = price + 40
        send_message(f"🎯 {symbol_name} BUY | TARGET: {target}")

    elif last['EMA9'] < last['EMA15']:
        target = price - 40
        send_message(f"🎯 {symbol_name} SELL | TARGET: {target}")

    # ===== 4️⃣ ORB (Opening Range Breakout) =====
    try:
        first_candle_high = df.iloc[0]['High']
        first_candle_low = df.iloc[0]['Low']

        if price > first_candle_high:
            send_message(f"🚀 {symbol_name} ORB BREAKOUT BUY @ {price}")

        elif price < first_candle_low:
            send_message(f"🚀 {symbol_name} ORB BREAKOUT SELL @ {price}")

    except:
        pass


# ===== START MESSAGE =====
send_message("✅ Bot Started - Live Market Tracking ON")

# ===== MAIN LOOP =====
while True:
    print("Checking signals...")

    check_signals("NIFTY", NIFTY)
    check_signals("BANKNIFTY", BANKNIFTY)

    time.sleep(60)   # runs every 1 minute
