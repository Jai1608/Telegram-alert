import os,threading,time,requests
from datetime import datetime
from flask import Flask,request as freq

app=Flask(__name__)
TOKEN=os.environ.get("TELEGRAM_BOT_TOKEN","")
CHAT=os.environ.get("TELEGRAM_CHAT_ID","")
state={"upper":float(os.environ.get("UPPER_BE","999999")),"lower":float(os.environ.get("LOWER_BE","1")),"price":0.0,"au":False,"al":False,"last":"Never","log":[]}

def lg(m):
    e=f"[{datetime.now().strftime('%H:%M:%S')}] {m}"
    print(e,flush=True)
    state["log"].insert(0,e)
    state["log"]=state["log"][:40]

def tg(msg,n=3):
    for i in range(n):
        try:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":msg,"parse_mode":"HTML"},timeout=10)
            lg(f"TG sent {i+1}/{n}")
        except Exception as e:
            lg(f"TG error:{e}")
        if i<n-1:time.sleep(3)

def get_price():
    try:
        r=requests.get("https://api.kraken.com/0/public/Ticker?pair=XBTUSD",timeout=15,headers={"User-Agent":"Mozilla/5.0"})
        p=float(r.json()["result"]["XXBTZUSD"]["c"][0])
        lg(f"Kraken OK: ${p:,.0f}")
        return p
    except Exception as e:
        lg(f"Kraken fail:{e}")
    try:
        r=requests.get("https://api-pub.bitfinex.com/v2/ticker/tBTCUSD",timeout=15,headers={"User-Agent":"Mozilla/5.0"})
        p=float(r.json()[6])
        lg(f"Bitfinex OK: ${p:,.0f}")
        return p
    except Exception as e:
        lg(f"Bitfinex fail:{e}")
    try:
        r=requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",timeout=15,headers={"User-Agent":"Mozilla/5.0"})
        p=float(r.json()["price"])
        lg(f"Binance OK: ${p:,.0f}")
        return p
    except Exception as e:
        lg(f"Binance fail:{e}")
    lg("ALL APIs FAILED")
    return None

def monitor():
    lg("Monitor thread started")
    tg(f"✅ <b>JK BTC Alert LIVE</b>\n📈 Upper: ${state['upper']:,.0f}\n📉 Lower: ${state['lower']:,.0f}\nMonitoring 24/7 🙏",n=1)
    while True:
        try:
            p=get_price()
            if p and p>0:
                state["price"]=p
                state["last"]=datetime.now().strftime("%H:%M:%S")
                u,l=state["upper"],state["lower"]
                if p>=u and not state["au"]:
                    tg(f"🔴🔴🔴 <b>MACHA WAKE UP! UPPER HIT!</b>\n⚡ BTC: ${p:,.0f}\nUpper BE: ${u:,.0f}\n🛠 Add adjustment NOW!",n=3)
                    state["au"]=True
                elif p<=l and not state["al"]:
                    tg(f"🔵🔵🔵 <b>MACHA WAKE UP! LOWER HIT!</b>\n⚡ BTC: ${p:,.0f}\nLower BE: ${l:,.0f}\n🛠 Add adjustment NOW!",n=3)
                    state["al"]=True
                elif p<u*0.99 and state["au"]:
                    state["au"]=False
                    tg(f"✅ Recovered below upper. BTC: ${p:,.0f}",n=1)
                elif p>l*1.01 and state["al"]:
                    state["al"]=False
                    tg(f"✅ Recovered above lower. BTC: ${p:,.0f}",n=1)
        except Exception as e:
            lg(f"Loop error:{e}")
        time.sleep(30)

@app.route("/")
def home():
    p=state["price"]
    u,l=state["upper"],state["lower"]
    logs="".join(f'<div style="padding:4px 0;border-bottom:1px solid #333;font-size:12px;color:#aaa;">{x}</div>'for x in state["log"][:20])
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/><meta http-equiv="refresh" content="30"/><title>JK BTC Alert</title>
<style>*{{margin:0;padding:0;box-sizing:border-box;}}body{{font-family:sans-serif;background:#0a0e1a;color:#fff;padding:20px;}}
.c{{background:#161a2b;border:1px solid #ffffff14;border-radius:12px;padding:16px;margin:12px 0;}}
.g{{color:#00d395;}}.r{{color:#ff4d4d;}}.gold{{color:#f7931a;font-size:22px;font-weight:700;}}
input{{background:#0a0e1a;border:1px solid #ffffff20;border-radius:8px;padding:10px;color:#fff;font-size:16px;width:100%;margin:6px 0;}}
button{{background:#f7931a;color:#0a0e1a;border:none;padding:12px;border-radius:8px;font-weight:700;width:100%;cursor:pointer;margin-top:6px;font-size:15px;}}
</style></head><body>
<h2 style="margin-bottom:16px;">🚨 JK BTC Alert</h2>
<div class="c"><div class="gold">${p:,.0f}</div>
<div style="margin-top:8px;font-size:14px;">Upper BE: <span class="{'r'if p>=u else'g'}">${u:,.0f}</span> &nbsp;|&nbsp; Lower BE: <span class="{'r'if p<=l else'g'}">${l:,.0f}</span></div>
<div style="font-size:12px;color:#666;margin-top:4px;">Last: {state['last']}</div></div>
<div class="c"><b>✏️ Update Levels</b>
<form action="/update" method="POST">
<label style="font-size:13px;color:#aaa;">Upper BE ($)</label><input name="upper" value="{u:.0f}"/>
<label style="font-size:13px;color:#aaa;">Lower BE ($)</label><input name="lower" value="{l:.0f}"/>
<button type="submit">💾 Save</button></form></div>
<div class="c"><b>📋 Log</b><br/><br/>{logs}</div>
<p style="color:#666;font-size:12px;text-align:center;margin-top:12px;">Auto-refreshes every 30s</p>
</body></html>"""

@app.route("/update",methods=["POST"])
def update():
    state["upper"]=float(freq.form.get("upper",state["upper"]))
    state["lower"]=float(freq.form.get("lower",state["lower"]))
    state["au"]=False
    state["al"]=False
    lg(f"Updated: Upper ${state['upper']:,.0f} | Lower ${state['lower']:,.0f}")
    tg(f"✏️ Levels updated\nUpper: ${state['upper']:,.0f}\nLower: ${state['lower']:,.0f}",n=1)
    return home()

@app.route("/ping")
def ping():
    return "OK"

threading.Thread(target=monitor,daemon=True).start()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))