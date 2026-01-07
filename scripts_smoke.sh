#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "[1] health"
curl -sS "$BASE_URL/health" | cat
echo

echo "[2] players"
curl -sS "$BASE_URL/gms/players" | cat
echo

echo "[3] metrics (first 20 lines)"
curl -sS "$BASE_URL/metrics" | head -n 20
echo
