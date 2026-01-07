import os
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from fastapi import FastAPI, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# -----------------------------
# Config (env-driven toggles)
# -----------------------------
ENV = os.getenv("ENV", "dev")
LOG_PATH = os.getenv("LOG_PATH", "logs/app.log")

SIMULATE_GMS_DOWN = os.getenv("SIMULATE_GMS_DOWN", "0") == "1"
SIMULATE_SLOW_GMS_MS = int(os.getenv("SIMULATE_SLOW_GMS_MS", "0"))  # e.g. 800

# -----------------------------
# Logging
# -----------------------------
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logger = logging.getLogger("casino-appsupport")
logger.setLevel(logging.INFO)

fmt = logging.Formatter("%(asctime)s | %(levelname)s | ENV=%(env)s | %(message)s")

# prevent duplicate handlers on reload
if not logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

def log(level: int, message: str):
    extra = {"env": ENV}
    logger.log(level, message, extra=extra)

# -----------------------------
# Metrics
# -----------------------------
app_requests_total = Counter("app_requests_total", "Total HTTP requests")
app_errors_total = Counter("app_errors_total", "Total application errors")
gms_down_total = Counter("gms_down_total", "Total simulated GMS down events")
gms_slow_total = Counter("gms_slow_total", "Total simulated slow GMS responses")

# -----------------------------
# App
# -----------------------------
app = FastAPI(title="casino-appsupport", version="0.1.0")

# Fake “GMS-like” in-memory data
PLAYERS: List[Dict[str, Any]] = [
    {"player_id": "P1001", "name": "Alex Chen", "tier": "Gold", "balance": 1250.75, "status": "ACTIVE"},
    {"player_id": "P1002", "name": "Sam Patel", "tier": "Platinum", "balance": 8020.10, "status": "ACTIVE"},
    {"player_id": "P1003", "name": "Jordan Smith", "tier": "Silver", "balance": 210.00, "status": "INACTIVE"},
]

@app.on_event("startup")
def on_startup():
    log(logging.INFO, "Startup complete | Service=casino-appsupport | Component=GMS-sim")

@app.get("/health")
def health():
    app_requests_total.inc()
    return {
        "status": "ok",
        "env": ENV,
        "ts": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "api": "ok",
            "gms_sim": "ok" if not SIMULATE_GMS_DOWN else "degraded",
        },
    }

@app.get("/gms/players")
def get_players():
    app_requests_total.inc()

    # simulate slow upstream dependency
    if SIMULATE_SLOW_GMS_MS > 0:
        gms_slow_total.inc()
        log(logging.WARNING, f"/gms/players | 200 | Simulated slow GMS ({SIMULATE_SLOW_GMS_MS}ms)")
        time.sleep(SIMULATE_SLOW_GMS_MS / 1000.0)

    # simulate upstream down
    if SIMULATE_GMS_DOWN:
        app_errors_total.inc()
        gms_down_total.inc()
        log(logging.ERROR, "/gms/players | 503 | Simulated GMS down")
        return Response(content='{"detail":"GMS unavailable (simulated)"}', status_code=503, media_type="application/json")

    log(logging.INFO, f"/gms/players | 200 | count={len(PLAYERS)}")
    return {"count": len(PLAYERS), "players": PLAYERS}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
