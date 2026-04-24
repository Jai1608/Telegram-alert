import os, requests
from datetime import datetime

TOKEN = os.environ["TOKEN"]
CHAT  = os.environ["CHAT"]
UPPER = 78270.0
LOWER = 78080.0

def get_price():
    r = requests.get(
        "https://api.kraken.com/0/public/Ticker?pair=XBTUSD",
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    return float(r.json()["result"]["XXBTZUSD"]["c"][0])

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"},
        timeout=10
    )

price = get_price()
now = datetime.now().strftime("%d %b %Y, %I:%M %p")
print(f"BTC: ${price:,.0f} | Upper: ${UPPER:,.0f} | Lower: ${LOWER:,.0f}")

if price >= UPPER:
    send(f"🔴🔴🔴 <b>MACHA WAKE UP! UPPER BE CROSSED!</b>\n\n"
         f"⚡ <b>BTC NOW: ${price:,.0f}</b>\n"
         f"📈 Upper BE: ${UPPER:,.0f}\n\n"
         f"🛠 Open Delta Exchange NOW!\n⏰ {now}")
elif price <= LOWER:
    send(f"🔵🔵🔵 <b>MACHA WAKE UP! LOWER BE CROSSED!</b>\n\n"
         f"⚡ <b>BTC NOW: ${price:,.0f}</b>\n"
         f"📉 Lower BE: ${LOWER:,.0f}\n\n"
         f"🛠 Open Delta Exchange NOW!\n⏰ {now}")
else:
    print(f"Safe. No alert.")
