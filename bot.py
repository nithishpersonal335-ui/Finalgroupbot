import requests
import time

# ✅ YOUR DETAILS
BOT_TOKEN = "8694926384:AAGE_6UPkci3OcS1_QzPu7Vj5nVoQnBYsvU"
CHAT_ID = "1207682165"

# ✅ TELEGRAM SEND FUNCTION
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        res = requests.post(url, data=data)
        print("Message sent:", res.text)
    except Exception as e:
        print("Error:", e)

# ✅ TEST ON START
def test_message():
    send_telegram_message("🚀 Bot Started Successfully!")

# ✅ SAMPLE SIGNALS LOOP (replace with your logic)
def run_bot():
    while True:
        print("Checking signals...")

        # 🔹 TYPE 1: EMA crossover
        send_telegram_message("📊 EMA 9/15 Crossover Signal")

        # 🔹 TYPE 2: Confirmed signal
        send_telegram_message("✅ Confirmed Trade Signal")

        # 🔹 TYPE 3: 40 points target
        send_telegram_message("🎯 40 Points Strategy Signal")

        # 🔹 TYPE 4: ORB breakout
        send_telegram_message("🔥 ORB Breakout Signal")

        time.sleep(5)  # every 1 minute

# 🚀 MAIN
if __name__ == "__main__":
    print("Bot Started...")
    test_message()
    run_bot()
