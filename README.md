# CivicFlow

An agentic civic operations system: five AI agents investigate, route, chase, verify and coordinate citizen grievances from report to verified closure, behind a public grievance portal. Humans approve every decision that affects a citizen's case.

> Student hackathon prototype — not an official website. "CivicFlow Municipal Corporation" is fictional.

Plan and rules: [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md) · [docs/CONTRACTS.md](docs/CONTRACTS.md) · [TASKS.md](TASKS.md) · [CLAUDE.md](CLAUDE.md)

## Getting started (no Docker experience needed)

Docker is only used to run the database. You don't write any Docker files.

1. Install **Docker Desktop**, **Python 3.11**, **Node.js 20+** and **Git**. On Windows, use WSL2 and run everything inside the Ubuntu terminal.
2. Open Docker Desktop once and leave it running (the whale icon in the menu bar or tray).
3. In a terminal, inside the project folder:
   ```bash
   make setup
   ```
   This creates `.env` from `.env.example`, a Python virtual environment, and installs everything. Open `.env` and fill in the empty values (passwords, keys).
4. Start the backend (it starts the database and applies migrations automatically):
   ```bash
   make api
   ```
   API docs: http://localhost:8000/docs
5. In a second terminal, start the website:
   ```bash
   make web
   ```
   Website: http://localhost:5173
6. Load the starting data:
   ```bash
   make seed
   ```

Other commands: `make test`, `make llm-check`, `make reset` (wipes the database), `make full` (everything in Docker).

If `make db` says it can't connect to Docker, Docker Desktop isn't running yet.
