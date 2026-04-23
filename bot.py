import requests
import time

# ===== CONFIG =====
BOT_TOKEN = "8694926384:AAGE_6UPkci3OcS1_QzPu7Vj5nVoQnBYsvU"
CHAT_ID = "1207682165"

# ===== TELEGRAM FUNCTION =====
def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    try:
        res = requests.post(url, data=data)
        print("Message:", res.text)
    except Exception as e:
        print("Error:", e)

# ===== START MESSAGE =====
send_message("✅ Bot Started & Running")

# ===== SIGNAL FUNCTIONS =====

# 1️⃣ EMA CROSSOVER (FULL DAY)
def ema_crossover():
    send_message("📊 EMA 9/15 Crossover Signal")

# 2️⃣ CONFIRMED SIGNAL
def confirmed_signal():
    send_message("✅ Confirmed Buy/Sell Signal")

# 3️⃣ 40 POINT TARGET SYSTEM
def target_40():
    send_message("🎯 40 Points Target Signal")

# 4️⃣ ORB SIGNAL
def orb_signal():
    send_message("🚀 ORB Breakout Signal")

# ===== TEST MESSAGE =====
def test_message():
    send_message("🧪 Test Message Working")

test_message()

# ===== MAIN LOOP =====
while True:
    # 👉 Replace below with your real market logic later

    ema_crossover()
    time.sleep(5)

    confirmed_signal()
    time.sleep(5)

    target_40()
    time.sleep(5)

    orb_signal()
    time.sleep(60)
