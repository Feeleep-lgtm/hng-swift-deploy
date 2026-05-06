from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import time, os, random
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest

app = FastAPI(title="SwiftDeploy API")

start_time = time.time()
MODE = os.getenv("MODE", "stable")
VERSION = os.getenv("APP_VERSION", "1.1.0")

http_requests = Counter('http_requests_total', 'Total HTTP requests', ['method', 'path', 'status'])
http_latency = Histogram('http_request_duration_seconds', 'Request latency', ['method', 'path'])
app_uptime = Gauge('app_uptime_seconds', 'Application uptime')
app_mode = Gauge('app_mode', 'Current mode', ['mode'])
chaos_active = Gauge('chaos_active', 'Chaos active', ['type'])

chaos_state = {"active": False, "mode": None, "duration": 0, "error_rate": 0.0}

@app.get("/")
@app.head("/")
async def root():
    start = time.time()
    http_requests.labels(method="GET", path="/", status=200).inc()
    
    if chaos_state["active"] and chaos_state["mode"] == "slow":
        time.sleep(chaos_state["duration"])
    elif chaos_state["active"] and chaos_state["mode"] == "error" and random.random() < chaos_state["error_rate"]:
        http_requests.labels(method="GET", path="/", status=500).inc()
        return JSONResponse(status_code=500, content={"error": "Chaos error injected"})

    http_latency.labels(method="GET", path="/").observe(time.time() - start)
    return {
        "message": f"SwiftDeploy API running in {MODE.upper()} mode",
        "mode": MODE,
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/healthz")
@app.head("/healthz")
async def healthz():
    http_requests.labels(method="GET", path="/healthz", status=200).inc()
    return {"status": "healthy", "mode": MODE}

@app.get("/metrics")
async def metrics():
    app_uptime.set(time.time() - start_time)
    app_mode.labels(mode=MODE).set(1 if MODE == "canary" else 0)
    chaos_active.labels(type=chaos_state.get("mode") or "none").set(1 if chaos_state["active"] else 0)
    return PlainTextResponse(generate_latest())

@app.post("/chaos")
async def chaos(request: Request):
    global chaos_state
    data = await request.json()
    if data.get("mode") == "recover":
        chaos_state = {"active": False, "mode": None, "duration": 0, "error_rate": 0.0}
        return {"status": "recovered"}
    chaos_state = {
        "active": True,
        "mode": data.get("mode"),
        "duration": data.get("duration", 0),
        "error_rate": data.get("rate", 0.5)
    }
    return {"status": "chaos activated", "config": chaos_state}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
EOFcat > app/main.py << 'EOF'
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import time, os, random
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest

app = FastAPI(title="SwiftDeploy API")

start_time = time.time()
MODE = os.getenv("MODE", "stable")
VERSION = os.getenv("APP_VERSION", "1.1.0")

http_requests = Counter('http_requests_total', 'Total HTTP requests', ['method', 'path', 'status'])
http_latency = Histogram('http_request_duration_seconds', 'Request latency', ['method', 'path'])
app_uptime = Gauge('app_uptime_seconds', 'Application uptime')
app_mode = Gauge('app_mode', 'Current mode', ['mode'])
chaos_active = Gauge('chaos_active', 'Chaos active', ['type'])

chaos_state = {"active": False, "mode": None, "duration": 0, "error_rate": 0.0}

@app.get("/")
@app.head("/")
async def root():
    start = time.time()
    http_requests.labels(method="GET", path="/", status=200).inc()
    
    if chaos_state["active"] and chaos_state["mode"] == "slow":
        time.sleep(chaos_state["duration"])
    elif chaos_state["active"] and chaos_state["mode"] == "error" and random.random() < chaos_state["error_rate"]:
        http_requests.labels(method="GET", path="/", status=500).inc()
        return JSONResponse(status_code=500, content={"error": "Chaos error injected"})

    http_latency.labels(method="GET", path="/").observe(time.time() - start)
    return {
        "message": f"SwiftDeploy API running in {MODE.upper()} mode",
        "mode": MODE,
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/healthz")
@app.head("/healthz")
async def healthz():
    http_requests.labels(method="GET", path="/healthz", status=200).inc()
    return {"status": "healthy", "mode": MODE}

@app.get("/metrics")
async def metrics():
    app_uptime.set(time.time() - start_time)
    app_mode.labels(mode=MODE).set(1 if MODE == "canary" else 0)
    chaos_active.labels(type=chaos_state.get("mode") or "none").set(1 if chaos_state["active"] else 0)
    return PlainTextResponse(generate_latest())

@app.post("/chaos")
async def chaos(request: Request):
    global chaos_state
    data = await request.json()
    if data.get("mode") == "recover":
        chaos_state = {"active": False, "mode": None, "duration": 0, "error_rate": 0.0}
        return {"status": "recovered"}
    chaos_state = {
        "active": True,
        "mode": data.get("mode"),
        "duration": data.get("duration", 0),
        "error_rate": data.get("rate", 0.5)
    }
    return {"status": "chaos activated", "config": chaos_state}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
