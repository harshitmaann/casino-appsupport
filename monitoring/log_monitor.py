import os
import time
from collections import deque
from typing import Deque, List

LOG_PATH = os.getenv("LOG_PATH", "logs/app.log")

ERROR_THRESHOLD = int(os.getenv("ERROR_THRESHOLD", "2"))
SLOW_THRESHOLD = int(os.getenv("SLOW_THRESHOLD", "1"))
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "5"))
WINDOW_LINES = int(os.getenv("WINDOW_LINES", "250"))

# What we consider "slow" for this repo:
# app/main.py logs a WARNING line containing: "Simulated slow GMS"
SLOW_MARKER = os.getenv("SLOW_MARKER", "Simulated slow GMS")

def tail_lines(path: str, n: int) -> List[str]:
    """
    Read last n lines from a file efficiently.
    """
    if n <= 0:
        return []
    if not os.path.exists(path):
        return []

    dq: Deque[str] = deque(maxlen=n)
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                dq.append(line.rstrip("\n"))
    except Exception:
        return []
    return list(dq)

def count_errors(lines: List[str]) -> int:
    """
    Count ERROR-level app log lines.
    """
    return sum(1 for l in lines if " | ERROR | " in l)

def count_slow(lines: List[str]) -> int:
    """
    Count simulated slow-response markers.
    """
    return sum(1 for l in lines if SLOW_MARKER in l)

def main():
    print(f"[INFO] log_monitor watching {LOG_PATH} every {INTERVAL_SECONDS}s")
    print(f"[INFO] thresholds: ERROR>={ERROR_THRESHOLD}, SLOW>={SLOW_THRESHOLD}")
    print(f"[INFO] window: last {WINDOW_LINES} total log lines")

    while True:
        window = tail_lines(LOG_PATH, WINDOW_LINES)
        errors = count_errors(window)
        slow = count_slow(window)

        if errors >= ERROR_THRESHOLD:
            print(f"[ALERT] log_monitor: ERROR threshold exceeded ({errors} in last {len(window)} lines)")
        elif slow >= SLOW_THRESHOLD:
            print(f"[ALERT] log_monitor: SLOW threshold exceeded ({slow} in last {len(window)} lines)")
        else:
            print(f"[OK] log_monitor: errors={errors}, slow={slow} (window={len(window)} lines)")

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
