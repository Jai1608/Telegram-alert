#!/usr/bin/env python3
"""
=================================================
  JK CRYPTO CAPITAL — BTC PRICE ALERT SYSTEM
  Monitors BTC price. Sends LOUD Telegram alert
  when price crosses your breakeven levels.
  Run this in Colab before you sleep.
=================================================
"""

import requests
import time
from datetime import datetime

# ================================================
# ✏️  EDIT THESE BEFORE RUNNING
# ================================================
TELEGRAM_BOT_TOKEN = "8498712330:AAEOvwG2T_cNAWSxMHFK8YIVdbl6UvtgMhI"   # from @BotFather
TELEGRAM_CHAT_ID   = "8498712330"     # your chat ID
UPPER_BREAKEVEN = 81600   # ← your upper breakeven price (USDT)
LOWER_BREAKEVEN = 73000   # ← your lower breakeven price (USDT)

CHECK_INTERVAL_SECONDS = 30   # check every 30 seconds
# ================================================

BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

alert_sent_upper = False
alert_sent_lower = False
check_count = 0

def get_btc_price():
    try:
        res = requests.get(BINANCE_URL, timeout=10)
        data = res.json()
        return float(data['price'])
    except Exception as e:
        print(f"  ⚠️  Price fetch error: {e}")
        return None

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print(f"  ✅ Telegram alert sent!")
        else:
            print(f"  ❌ Telegram error: {res.text}")
    except Exception as e:
        print(f"  ❌ Telegram send failed: {e}")

def format_price(p):
    return f"${p:,.0f}"

def run_monitor():
    global alert_sent_upper, alert_sent_lower, check_count

    print("=" * 55)
    print("  🚨 JK CRYPTO CAPITAL — BTC PRICE ALERT MONITOR")
    print("=" * 55)
    print(f"  📈 Upper Breakeven : {format_price(UPPER_BREAKEVEN)}")
    print(f"  📉 Lower Breakeven : {format_price(LOWER_BREAKEVEN)}")
    print(f"  🔄 Check interval  : every {CHECK_INTERVAL_SECONDS}s")
    print("=" * 55)
    print("  ✅ Monitoring started. Keep Colab tab open.")
    print("  🛑 To stop: Runtime → Interrupt Execution")
    print("=" * 55)

    # Send a startup confirmation to Telegram
    startup_msg = (
        "✅ <b>JK Crypto Capital — Price Monitor ACTIVE</b>\n\n"
        f"📈 Upper alert: <b>{format_price(UPPER_BREAKEVEN)}</b>\n"
        f"📉 Lower alert: <b>{format_price(LOWER_BREAKEVEN)}</b>\n\n"
        "Monitoring BTC every 30s. Will alert if price crosses either level.\n"
        "Sleep well macha 🙏"
    )
    send_telegram(startup_msg)

    while True:
        check_count += 1
        price = get_btc_price()
        now = datetime.now().strftime("%H:%M:%S")

        if price is None:
            print(f"  [{now}] ⚠️  Could not fetch price. Retrying...")
            time.sleep(CHECK_INTERVAL_SECONDS)
            continue

        # Calculate distance from breakevens
        dist_upper = ((UPPER_BREAKEVEN - price) / UPPER_BREAKEVEN) * 100
        dist_lower = ((price - LOWER_BREAKEVEN) / LOWER_BREAKEVEN) * 100

        print(f"  [{now}] BTC: {format_price(price)}  |  "
              f"Upper: {dist_upper:+.1f}%  |  Lower: {dist_lower:+.1f}%", end="")

        # ─── UPPER BREAKEVEN BREACH ─────────────────────
        if price >= UPPER_BREAKEVEN and not alert_sent_upper:
            print("  🔴 UPPER BREAKEVEN BREACHED!")
            alert_msg = (
                "🔴🔴🔴 <b>WAKE UP MACHA! UPPER BREAKEVEN HIT!</b> 🔴🔴🔴\n\n"
                f"📍 <b>BTC Current Price: {format_price(price)}</b>\n"
                f"⬆️ Upper Breakeven: {format_price(UPPER_BREAKEVEN)}\n\n"
                "❗️ BTC has CROSSED your upper breakeven.\n"
                "🛠️ Time to add Leg2 / Leg3 adjustment!\n\n"
                f"⏰ Time: {now}"
            )
            # Send 3 times for maximum noise
            for i in range(3):
                send_telegram(alert_msg)
                time.sleep(2)
            alert_sent_upper = True

        # ─── LOWER BREAKEVEN BREACH ─────────────────────
        elif price <= LOWER_BREAKEVEN and not alert_sent_lower:
            print("  🔵 LOWER BREAKEVEN BREACHED!")
            alert_msg = (
                "🔵🔵🔵 <b>WAKE UP MACHA! LOWER BREAKEVEN HIT!</b> 🔵🔵🔵\n\n"
                f"📍 <b>BTC Current Price: {format_price(price)}</b>\n"
                f"⬇️ Lower Breakeven: {format_price(LOWER_BREAKEVEN)}\n\n"
                "❗️ BTC has CROSSED your lower breakeven.\n"
                "🛠️ Time to add Leg2 / Leg3 adjustment!\n\n"
                f"⏰ Time: {now}"
            )
            for i in range(3):
                send_telegram(alert_msg)
                time.sleep(2)
            alert_sent_lower = True

        # ─── RECOVERY — reset alert if price comes back inside ──
        elif price < (UPPER_BREAKEVEN * 0.99) and alert_sent_upper:
            print("  ✅ Price back inside upper range. Alert reset.")
            send_telegram(
                f"✅ BTC back below upper BE\n"
                f"Price: {format_price(price)}\n"
                f"Upper was: {format_price(UPPER_BREAKEVEN)}"
            )
            alert_sent_upper = False

        elif price > (LOWER_BREAKEVEN * 1.01) and alert_sent_lower:
            print("  ✅ Price back inside lower range. Alert reset.")
            send_telegram(
                f"✅ BTC back above lower BE\n"
                f"Price: {format_price(price)}\n"
                f"Lower was: {format_price(LOWER_BREAKEVEN)}"
            )
            alert_sent_lower = False

        else:
            print()  # newline after status

        time.sleep(CHECK_INTERVAL_SECONDS)

# Run it
run_monitor()
