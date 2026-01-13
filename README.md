# Casino AppSupport

[![ci](https://github.com/harshitmaann/casino-appsupport/actions/workflows/ci.yml/badge.svg)](https://github.com/harshitmaann/casino-appsupport/actions/workflows/ci.yml)

A small application support and incident response lab that simulates a casino style upstream dependency (GMS-like service) and exposes health checks, logs, and Prometheus metrics.

This project is built to show how I think and work in application support: reproduce incidents, observe symptoms, identify root cause signals, and validate fixes with metrics and logs.

**Runbook:** [docs/RUNBOOK.md](docs/RUNBOOK.md)

## What this demonstrates

- Incident triage under upstream failures (503 responses) and latency spikes
- Basic service observability (logs you can tail plus Prometheus metrics)
- Simple operational tooling (a log monitor that alerts on error and slow patterns)
- Practical FastAPI operations (local dev, environment driven behavior, clean endpoints)

## Repository layout

- `app/main.py`
  - FastAPI service that simulates an upstream dependency and emits logs and metrics
- `monitoring/log_monitor.py`
  - Tails `logs/app.log` and prints alerts when thresholds are exceeded
- `logs/`
  - Local log output (kept out of git except for `.gitkeep`)

## API endpoints

- `GET /health`
  - Basic service health response
- `GET /gms/players`
  - Simulates an upstream dependency with three modes:
    - Normal success
    - Slow upstream
    - Upstream down (503)
- `GET /metrics`
  - Prometheus metrics endpoint (from `prometheus-client`)

## Quickstart

### 1) Set up a virtual environment

```bash
cd ~/casino-appsupport
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run the API

```bash
mkdir -p logs
: > logs/app.log
uvicorn app.main:app --reload
```

Test it:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/gms/players
curl -s http://127.0.0.1:8000/metrics | head
```

## Simulating incidents

The API behavior can be driven by environment variables.

### Simulate upstream down

```bash
: > logs/app.log
SIMULATE_GMS_DOWN=1 uvicorn app.main:app --reload
```

Then hit:

```bash
curl -i http://127.0.0.1:8000/gms/players
```

You should see 503 responses and corresponding logs and metrics.

### Simulate slow upstream

```bash
: > logs/app.log
SIMULATE_SLOW_GMS_MS=800 uvicorn app.main:app --reload
```

Then hit:

```bash
curl -s http://127.0.0.1:8000/gms/players
```

## Log monitoring

The log monitor reads a sliding window of recent log lines from `logs/app.log` and prints:

- `[OK]` when error and slow patterns are under thresholds
- `[ALERT]` when thresholds are exceeded

Run it in a second terminal:

```bash
source .venv/bin/activate
python monitoring/log_monitor.py
```

Tip: While the monitor is running, trigger traffic to `/gms/players` and watch the alert state change.

## Notes for viewers

If you are reviewing this as an application support sample, here is what to look for:

- Clear reproduction steps for failure modes (down vs slow)
- Observable signals (logs plus metrics) that match each incident mode
- A small operational tool (`log_monitor.py`) that mimics on-call alerting logic

## Next improvements

- Add request correlation IDs and structured JSON logging
- Add a simple dashboard example (Grafana) and a few sample Prometheus alert rules
- Add tests for endpoints and incident toggles

## License

MIT
