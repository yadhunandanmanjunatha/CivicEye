# CLAUDE.md: rules for every AI coding session on CivicFlow

CivicFlow is a multi-agent civic grievance system (citizen portal, officer console, field team app, control room, partner agency portal) with 5 AI agents. This is a 24-hour hackathon build by **two people on two laptops, each with one Claude Code session**. Lane A = Person A, Lane B = Person B.

## Read this first, then only what your task needs
- `docs/BUILD_PLAN.md` §0 has the team decisions. They override everything else.
- `docs/CONTRACTS.md` lists the shared interfaces. **Do not change them** (see "Contracts" below).
- `TASKS.md` has the task list: do **only** the task you were given.
- Don't scan or summarise the whole repo. Open only the files your task names.

## Lanes and file ownership

| Lane | Owns (may edit) | Must not edit |
|---|---|---|
| **A: Backend & Agents** | `backend/**` except `backend/app/seed/**` and `backend/tests/seed/**`; `docker-compose.yml`, `Makefile`, `.env.example`, `.github/**` | `web/**`, `simulator/**`, `e2e/**`, `backend/app/seed/**` |
| **B: Frontend & Data** | `web/**`, `simulator/**`, `e2e/**`, `backend/app/seed/**` (loader **and** data files), `backend/tests/seed/**`, `fixtures/photos/**`, `docs/DEMO_SCRIPT.md` | everything else in `backend/`, `docker-compose.yml`, `Makefile`, `.env.example` |

- Shared docs (`docs/CONTRACTS.md`, `TASKS.md`, `PROGRESS.md`): edit **only your own lane's section**, except for contract PRs.
- **Need a change in the other lane's files** (a compose service, a Makefile target, a new endpoint, a new field)? Don't make it. Write a short request under "Requests" in `PROGRESS.md` and tell your human, who passes it on.

## Contracts
- Any **rename, removal or type change** in `docs/CONTRACTS.md` (endpoint, field, enum, event, agent output schema, env var) needs a PR titled `contract: …` that both lane drivers approve. Stop and ask your human before starting one.
- **Adding** an optional field or a new endpoint is a minor change: allowed, but list it in your PR description.
- Lane B: never hand-edit `web/src/api/types.ts`. Regenerate it with `npm run gen:api`.

## Non-negotiable product rules
1. **Nothing for show.** Every button, number, link and page shown in the UI must work end to end. If it can't be finished, don't render it. No placeholder data in the UI, no "coming soon".
2. **No government labels.** No "Government of …", no emblems, no fake helpline numbers. The identity is the fictional "CivicFlow Municipal Corporation", plus the banner "Student hackathon prototype — not an official website."
3. **UI style:** a plain public-portal look (navy `#1b3a6b`, white, grey `#f2f2f2` panels, saffron `#e87722` accents), 0–3 px corners, bordered tables with S.No. and pagination, fieldset forms. **No** Tailwind/shadcn/MUI, gradients, glassmorphism, emoji or chat-box UI, and no "AI" wording: use "System Analysis" / "Auto-check result".
4. **Agents propose; code enforces.** Agents act only through domain services (`transition()`, `create_work_order()` and so on), never through direct ORM writes. Agents can never REJECT or CLOSE a complaint. Guardrail thresholds live inside the tools.
5. **Works with any LLM, or none.** Use only `LLMClient`; never import a provider SDK anywhere else. Every agent must work with `AGENT_MODE=rules`. Tests never call a real LLM: use `AGENT_MODE=rules` or the FakeLLM fixture.
6. **Privacy:** field teams never receive reporter phone numbers. Ingestion rejects VIN/phone/name fields. No secrets in code; config comes from `.env`.
7. Keep agent effort on the scenarios in BUILD_PLAN §6 and the demo story. Don't build handling for rare edge cases nobody asked for.

## Tech (no new dependencies without asking the human)
Backend: Python 3.11, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PostgreSQL 16 + PostGIS, APScheduler, Pillow, piexif, imagehash, `openai` + `anthropic` SDKs (inside `adapters/llm.py` only), python-jose, passlib[bcrypt], pytest, freezegun, httpx.
Frontend: React + Vite + TypeScript, React Router, CSS modules, Leaflet + leaflet.heat, Chart.js, react-i18next, openapi-typescript (dev), Playwright.
uvicorn runs with **one worker** (the scheduler and event bus are in-process).

## Commands
All commands go through **`dev.py`** (cross-platform). Lane A develops on macOS, Lane B on **Windows**. Don't write shell-only scripts (`bash`, `&&` chains in package.json, `rm -rf`); use Node or Python so they work on both. On Windows, run `py dev.py <cmd>`; on macOS, `python3 dev.py <cmd>` or `make <cmd>`.
```
dev.py setup                 # .env + venv + pip install + npm install
dev.py db                    # PostGIS in Docker on port 5433 (Docker runs only the database)
dev.py api                   # db + migrations + uvicorn --reload on :8000 (1 worker)
dev.py web                   # npm run dev on :5173
dev.py seed                  # reset + seed (idempotent, fixed IDs)
dev.py test                  # backend pytest (+ e2e when present)
dev.py llm-check             # test each configured LLM provider
dev.py full                  # everything in containers (built at the end, for judges)
cd web && npm run gen:api    # regenerate frontend types from the running API
```
The backend virtual env is `backend/.venv` (`Scripts\python.exe` on Windows, `bin/python` on macOS).

## How to work (to save usage)
- One task at a time. Start a fresh session or run `/clear` between tasks; use `/compact` if a task runs long.
- Before you code, state in 3–5 lines which files you'll touch. If any are outside your lane, stop and ask.
- Write tests with the code. Run `make test` (or that lane's subset) before saying you're done.
- **Never commit, push, create branches, or merge** unless your human asks in that message.
- When you finish: report what changed, how to verify it (exact command or click path), and what's left. Add 2–4 lines to your lane's section in `PROGRESS.md`.
- If something in the docs seems wrong or missing, ask. Don't invent architecture.
