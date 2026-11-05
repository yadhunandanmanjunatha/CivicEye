# CivicFlow developer commands. Works on macOS and Linux/WSL.
PYTHON ?= python3.11
VENV    = backend/.venv
BIN     = $(VENV)/bin

.PHONY: setup db api web migrate seed demo test llm-check reset full

setup:            ## create Python venv, install backend + web dependencies, create .env
	@test -f .env || cp .env.example .env
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -q --upgrade pip
	$(BIN)/pip install -q -e "backend[dev]"
	@if [ -f web/package.json ]; then cd web && npm install; fi

db:               ## start PostGIS in Docker (port 5433)
	docker compose up -d --wait db

migrate: db       ## apply database migrations
	cd backend && .venv/bin/alembic upgrade head

api: migrate      ## run the backend with auto-reload on http://localhost:8000
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000 --workers 1

web:              ## run the website on http://localhost:5173
	cd web && npm run dev

seed: migrate     ## reset demo data (idempotent, fixed IDs)
	cd backend && .venv/bin/python -m app.seed

demo: seed        ## seed and print the demo steps
	@cat docs/DEMO_SCRIPT.md 2>/dev/null || echo "docs/DEMO_SCRIPT.md not written yet"

test: db          ## run backend tests (+ e2e if web/e2e exist)
	cd backend && .venv/bin/pytest
	@if [ -f e2e/package.json ]; then cd e2e && npx playwright test; fi

llm-check:        ## check which configured LLM providers work
	cd backend && .venv/bin/python -m scripts.llm_check

reset:            ## delete the database volume (all data!)
	docker compose down -v

full:             ## everything in Docker (for judges)
	docker compose --profile full up --build
