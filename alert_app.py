import os, threading, time, requests
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
state = {
    "upper_be": float(os.environ.get("UPPER_BE", "99999999")),
    "lower_be": float(os.environ.get("LOWER_BE", "0")),
    "current_price": 0.0,
    "alert_upper": False,
    "alert_lower": False,
    "last_check": "Never",
    "log": []
}

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)
    state["log"].insert(0, entry)
    if len(state["log"]) > 50:
        state["log"] = state["log"][:50]

def get_price():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
        return float(r.json()["bitcoin"]["usd"])
    except:
        return None

def send_tg(msg, repeat=3):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for i in range(repeat):
        try:
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
        except:
            pass
        if i < repeat - 1:
            time.sleep(3)

def monitor():
    log("Monitor started")
    send_tg(
        f"✅ <b>JK BTC Alert LIVE on Render</b>\n\n"
        f"📈 Upper BE: <b>${state['upper_be']:,.0f}</b>\n"
        f"📉 Lower BE: <b>${state['lower_be']:,.0f}</b>\n\n"
        f"Monitoring 24/7. Will alert anytime BTC breaks out 🙏",
        repeat=1
    )
    while True:
        price = get_price()
        if price:
            state["current_price"] = price
            state["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            upper = state["upper_be"]
            lower = state["lower_be"]
            log(f"BTC: ${price:,.0f} | Upper: ${upper:,.0f} | Lower: ${lower:,.0f}")

            if price >= upper and not state["alert_upper"]:
                log(f"🔴 UPPER BREACHED! ${price:,.0f}")
                send_tg(
                    f"🔴🔴🔴 <b>MACHA WAKE UP! UPPER BE CROSSED!</b> 🔴🔴🔴\n\n"
                    f"⚡ <b>BTC NOW: ${price:,.0f}</b>\n"
                    f"📈 Your Upper BE: ${upper:,.0f}\n\n"
                    f"🛠 Open Delta Exchange → Add adjustment NOW!\n"
                    f"⏰ {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
                    repeat=3
                )
                state["alert_upper"] = True

            elif price <= lower and not state["alert_lower"]:
                log(f"🔵 LOWER BREACHED! ${price:,.0f}")
                send_tg(
                    f"🔵🔵🔵 <b>MACHA WAKE UP! LOWER BE CROSSED!</b> 🔵🔵🔵\n\n"
                    f"⚡ <b>BTC NOW: ${price:,.0f}</b>\n"
                    f"📉 Your Lower BE: ${lower:,.0f}\n\n"
                    f"🛠 Open Delta Exchange → Add adjustment NOW!\n"
                    f"⏰ {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
                    repeat=3
                )
                state["alert_lower"] = True

            elif price < (upper * 0.99) and state["alert_upper"]:
                state["alert_upper"] = False
                send_tg(f"✅ BTC back below upper BE. Price: ${price:,.0f}", repeat=1)

            elif price > (lower * 1.01) and state["alert_lower"]:
                state["alert_lower"] = False
                send_tg(f"✅ BTC back above lower BE. Price: ${price:,.0f}", repeat=1)

        time.sleep(30)

@app.route("/")
def home():
    p = state["current_price"]
    upper = state["upper_be"]
    lower = state["lower_be"]
    log_html = "".join(f'<div style="padding:4px 0;border-bottom:1px solid #1c2138;font-size:12px;color:#a0a9bf;">{l}</div>' for l in state["log"][:20])
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/>
    <meta http-equiv="refresh" content="30"/>
    <title>JK BTC Alert</title>
    <style>body{{font-family:sans-serif;background:#0a0e1a;color:#fff;padding:24px;}}
    .card{{background:#161a2b;border:1px solid #ffffff14;border-radius:12px;padding:20px;margin:12px 0;}}
    .green{{color:#00d395;}}.red{{color:#ff4d4d;}}.gold{{color:#f7931a;}}
    input{{background:#0a0e1a;border:1px solid #ffffff20;border-radius:8px;padding:10px;color:#fff;font-size:16px;width:100%;margin:8px 0;}}
    button{{background:#f7931a;color:#0a0e1a;border:none;padding:12px 24px;border-radius:8px;font-weight:700;font-size:15px;width:100%;cursor:pointer;margin-top:8px;}}
    </style></head><body>
    <h2>🚨 JK BTC Price Alert</h2>
    <div class="card"><b>BTC Price:</b> <span class="gold">${p:,.0f}</span><br/>
    <b>Upper BE:</b> <span class="{'red' if p>=upper else 'green'}">${upper:,.0f}</span><br/>
    <b>Lower BE:</b> <span class="{'red' if p<=lower else 'green'}">${lower:,.0f}</span><br/>
    <b>Last Check:</b> {state['last_check']}</div>
    <div class="card"><b>✏️ Update Levels</b>
    <form action="/update" method="POST">
    <label>Upper BE ($)</label><input name="upper" value="{upper:.0f}"/>
    <label>Lower BE ($)</label><input name="lower" value="{lower:.0f}"/>
    <button type="submit">💾 Save & Update</button></form></div>
    <div class="card"><b>📋 Log</b><br/>{log_html}</div>
    <p style="color:#6b7280;font-size:12px;text-align:center;">Auto-refreshes every 30s</p>
    </body></html>"""

@app.route("/update", methods=["POST"])
def update():
    state["upper_be"] = float(request.form.get("upper", state["upper_be"]))
    state["lower_be"] = float(request.form.get("lower", state["lower_be"]))
    state["alert_upper"] = False
    state["alert_lower"] = False
    log(f"Levels updated: Upper ${state['upper_be']:,.0f} | Lower ${state['lower_be']:,.0f}")
    send_tg(f"✏️ Levels updated\nUpper: ${state['upper_be']:,.0f}\nLower: ${state['lower_be']:,.0f}", repeat=1)
    return home()

@app.route("/ping")
def ping():
    return "OK"

threading.Thread(target=monitor, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
