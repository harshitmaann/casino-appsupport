.PHONY: venv install run run-down run-slow monitor lint

venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && pip install -r requirements.txt

run:
	. .venv/bin/activate && mkdir -p logs && : > logs/app.log && uvicorn app.main:app --reload

run-down:
	. .venv/bin/activate && mkdir -p logs && : > logs/app.log && SIMULATE_GMS_DOWN=1 uvicorn app.main:app --reload

run-slow:
	. .venv/bin/activate && mkdir -p logs && : > logs/app.log && SIMULATE_SLOW_GMS_MS=800 uvicorn app.main:app --reload

monitor:
	. .venv/bin/activate && python monitoring/log_monitor.py

lint:
	. .venv/bin/activate && python -m py_compile app/main.py monitoring/log_monitor.py
