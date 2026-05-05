from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time, os, random
from datetime import datetime

app = FastAPI(title="SwiftDeploy API")
start_time = time.time()

MODE = os.getenv("MODE", "stable")
VERSION = os.getenv("APP_VERSION", "1.0.0")

# Chaos configuration
chaos_state = {"active": False, "mode": None, "duration": 0, "error_rate": 0.0}

@app.get("/")
async def root():
    # Simulate chaos if active
    if chaos_state["active"]:
        if chaos_state["mode"] == "slow":
            time.sleep(chaos_state["duration"])
        elif chaos_state["mode"] == "error" and random.random() < chaos_state["error_rate"]:
            return JSONResponse(status_code=500, content={"error": "Chaos error injected"})

    return {
        "message": f"SwiftDeploy API running in {MODE.upper()} mode",
        "mode": MODE,
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": round(time.time() - start_time, 2)
    }

@app.get("/healthz")
async def healthz():
    return {
        "status": "healthy",
        "mode": MODE,
        "uptime_seconds": round(time.time() - start_time, 2)
    }

@app.post("/chaos")
async def trigger_chaos(request: Request):
    global chaos_state
    data = await request.json()
    
    if data.get("mode") == "recover":
        chaos_state = {"active": False, "mode": None, "duration": 0, "error_rate": 0.0}
        return {"status": "chaos recovered"}
    
    chaos_state = {
        "active": True,
        "mode": data.get("mode"),
        "duration": int(data.get("duration", 0)),
        "error_rate": float(data.get("rate", 0.5))
    }
    return {"status": "chaos activated", "config": chaos_state}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
