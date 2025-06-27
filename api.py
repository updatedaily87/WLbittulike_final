from fastapi import FastAPI, Query
import json
import asyncio
from wlbittu_real_like import login_guest, send_like
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

with open("guest_accounts.json") as f:
    ACCOUNTS = json.load(f)["accounts"]

try:
    with open("guest_state.json") as f:
        STATE = json.load(f)
except:
    STATE = {"used_accounts": []}
    with open("guest_state.json", "w") as f:
        json.dump(STATE, f)

@app.get("/like")
async def like(uid: str = Query(...), region: str = Query(...), key: str = Query(...)):
    if key != "wlbittu":
        return {"error": "unauthorized"}

    results = []
    used = set(STATE["used_accounts"])
    available_accounts = [acc for acc in ACCOUNTS if acc["uid"] not in used]

    for acc in available_accounts:
        try:
            login = await login_guest(acc["uid"], acc["password"])
            token = login.get("token")
            if not token:
                results.append({"uid": acc["uid"], "status": "login_failed"})
                continue

            liked = await send_like(token, uid)
            results.append({"uid": acc["uid"], "status": "liked" if liked.get("success") else "failed"})
            STATE["used_accounts"].append(acc["uid"])
        except Exception as e:
            results.append({"uid": acc["uid"], "status": f"error: {str(e)}"})

    with open("guest_state.json", "w") as f:
        json.dump(STATE, f)

    total = len([r for r in results if r["status"] == "liked"])
    return {
        "LikesGivenByAPI": total,
        "target_uid": uid,
        "details": results
    }

def reset_guest_state():
    with open("guest_state.json", "w") as f:
        json.dump({"used_accounts": []}, f)

scheduler = BackgroundScheduler()
scheduler.add_job(reset_guest_state, "cron", hour=1, minute=30)
scheduler.start()