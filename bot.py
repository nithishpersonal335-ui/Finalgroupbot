import requests
import pandas as pd
import time
from datetime import datetime

# ===== YOUR DETAILS =====
BOT_TOKEN = "8694926384:AAENkkCI4qoQOuWucP2OI4hCbtGG9Q9UFWw"
CHAT_ID = "1207682165"

# ===== TELEGRAM FUNCTION =====
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=data)
        print("Message:", r.text)
    except Exception as e:
        print("Error:", e)

# ===== START + TEST =====
def start_messages():
    send_telegram("🚀 Bot Started Successfully")
    send_telegram("✅ Test Message: Bot is working")

# ===== FETCH DATA =====
def get_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
    res = requests.get(url).json()

    closes = res['chart']['result'][0]['indicators']['quote'][0]['close']
    df = pd.DataFrame(closes, columns=['close'])
    df.dropna(inplace=True)

    return df

# ===== INDICATORS =====
def calculate(df):
    df['ema9'] = df['close'].ewm(span=9).mean()
    df['ema15'] = df['close'].ewm(span=15).mean()
    df['vwap'] = df['close'].expanding().mean()
    return df

# ===== SIGNAL LOGIC =====
def check_signal(name, symbol):
    df = get_data(symbol)
    df = calculate(df)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    signals = []

    # 1️⃣ EMA CROSSOVER
    if prev['ema9'] < prev['ema15'] and last['ema9'] > last['ema15']:
        signals.append(f"{name} 🟢 BUY (EMA CROSS)")
    elif prev['ema9'] > prev['ema15'] and last['ema9'] < last['ema15']:
        signals.append(f"{name} 🔴 SELL (EMA CROSS)")

    # 2️⃣ CONFIRMATION
    if last['ema9'] > last['ema15'] and last['close'] > last['vwap']:
        signals.append(f"{name} ✅ CONFIRMED BUY")
    elif last['ema9'] < last['ema15'] and last['close'] < last['vwap']:
        signals.append(f"{name} ❌ CONFIRMED SELL")

    # 3️⃣ 40 POINT TARGET SYSTEM
    if last['ema9'] > last['ema15']:
        signals.append(f"{name} 🎯 TARGET BUY (+40)")
    elif last['ema9'] < last['ema15']:
        signals.append(f"{name} 🎯 TARGET SELL (+40)")

    # 4️⃣ ORB BREAKOUT
    high = df['close'].iloc[:5].max()
    low = df['close'].iloc[:5].min()

    if last['close'] > high:
        signals.append(f"{name} 🚀 ORB BREAKOUT BUY")
    elif last['close'] < low:
        signals.append(f"{name} 💥 ORB BREAKOUT SELL")

    return signals

# ===== MAIN LOOP =====
def run_bot():
    start_messages()

    while True:
        try:
            now = datetime.now()

            # Market hours (9:15 to 3:30)
            if 9 <= now.hour <= 15:
                all_signals = []

                all_signals += check_signal("NIFTY", "^NSEI")
                all_signals += check_signal("BANKNIFTY", "^NSEBANK")

                if all_signals:
                    message = "\n".join(all_signals)
                    send_telegram(message)

            time.sleep(60)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

# ===== START BOT =====
run_bot()
