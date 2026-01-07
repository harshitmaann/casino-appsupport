# RUNBOOK: Casino AppSupport (GMS Simulator)

Purpose
- Quickly determine if the service is healthy, slow, or failing due to the simulated upstream dependency.
- Mirror real Application Support triage: reproduce, observe symptoms, validate with logs and metrics, and document next steps.

Incident modes and symptoms

1) Normal
- /health returns 200
- /gms/players returns 200 quickly
- logs show 200 responses
- metrics show low error counts and no slow/down spikes

2) Slow upstream
- /gms/players returns 200 but takes noticeably longer
- logs include: Simulated slow GMS
- metrics show an increase in slow events

3) Upstream down
- /gms/players returns 503
- logs include: Simulated GMS down
- metrics show increased errors and down events

------------------------------------------------------------

Quick checks (fastest path)

A) Is the service up?
Command:
curl -i http://127.0.0.1:8000/health

Expected:
HTTP/1.1 200 OK

B) Is the upstream endpoint working?
Command:
curl -i http://127.0.0.1:8000/gms/players

Expected:
- Normal: HTTP/1.1 200 OK
- Upstream down mode: HTTP/1.1 503 Service Unavailable

C) Check logs for errors and slow signals
Command:
tail -n 60 logs/app.log

Look for:
- 503 | Simulated GMS down
- Simulated slow GMS
- repeated 5xx patterns

D) Check metrics quickly (sanity)
Command:
curl -sS http://127.0.0.1:8000/metrics | egrep "app_errors_total|gms_down_total|gms_slow_total" || true

Interpretation:
- app_errors_total increases when the API returns 5xx
- gms_down_total increases during simulated upstream down
- gms_slow_total increases during simulated slow upstream

------------------------------------------------------------

Recovery actions (simulation toggles)

1) Start in normal mode
Commands:
: > logs/app.log
uvicorn app.main:app --reload

2) Simulate upstream down (503)
Commands:
: > logs/app.log
SIMULATE_GMS_DOWN=1 uvicorn app.main:app --reload

Validate:
curl -i http://127.0.0.1:8000/gms/players
tail -n 30 logs/app.log
curl -sS http://127.0.0.1:8000/metrics | egrep "app_errors_total|gms_down_total" || true

3) Simulate slow upstream
Commands:
: > logs/app.log
SIMULATE_SLOW_GMS_MS=800 uvicorn app.main:app --reload

Validate:
time curl -sS http://127.0.0.1:8000/gms/players >/dev/null
tail -n 30 logs/app.log
curl -sS http://127.0.0.1:8000/metrics | egrep "gms_slow_total" || true

------------------------------------------------------------

Escalation guidance (what to say)

When escalating (to dev, vendor, or infra), include:
- What changed (normal vs slow vs down)
- timestamps and sample log lines
- evidence (HTTP status, curl output, metrics counters)
- scope (is it only /gms/players or also /health?)

Example escalation note:
At 00:25, /gms/players began returning 503 consistently. /health remains 200. Logs show Simulated GMS down and metrics gms_down_total increased. Likely upstream dependency failure or forced-down mode. Request upstream validation.

------------------------------------------------------------

Optional: repo scripts

Smoke test:
./scripts/smoke.sh

Log monitor:
python monitoring/log_monitor.py
