# CivicFlow

An agentic civic operations system: five AI agents investigate, route, chase, verify and coordinate citizen grievances from report to verified closure, behind a public grievance portal. Humans approve every decision that affects a citizen's case.

> Student hackathon prototype — not an official website. "CivicFlow Municipal Corporation" is fictional.

Plan and rules: [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md) · [docs/CONTRACTS.md](docs/CONTRACTS.md) · [TASKS.md](TASKS.md) · [CLAUDE.md](CLAUDE.md)

## Getting started (no Docker experience needed)

Docker is only used to run the database. You don't write any Docker files.

All commands go through `dev.py`, which works the same on every system:

| System | How to run a command |
|---|---|
| **Windows** (PowerShell, cmd or Git Bash) | `py dev.py <command>`, or `python dev.py <command>` |
| **macOS / Linux** | `python3 dev.py <command>`, or the shortcut `make <command>` |

1. Install **Docker Desktop**, **Python 3.11 or newer**, **Node.js 20+** and **Git**. On Windows, tick "Add python.exe to PATH" in the Python installer.
2. Open Docker Desktop once and leave it running until it says "Engine running".
3. In a terminal inside the project folder, run `setup`:
   ```bash
   py dev.py setup
   ```
   This creates `.env` from `.env.example`, a Python virtual environment, and installs everything. Open `.env` and fill in the empty values (passwords, keys).
4. Start the backend (it starts the database and applies migrations automatically):
   ```bash
   py dev.py api
   ```
   API docs: http://localhost:8000/docs
5. In a second terminal, start the website:
   ```bash
   py dev.py web
   ```
   Website: http://localhost:5173
6. Load the starting data:
   ```bash
   py dev.py seed
   ```

Other commands: `test`, `llm-check`, `reset` (wipes the database), `full` (everything in Docker). Run `py dev.py` with no command to see the list.

If `db` says Docker isn't running, open Docker Desktop and wait for "Engine running".

### Windows: "An Application Control policy has blocked this file"

Some Windows laptops block Python and Node's compiled files. If you see this error, use **Docker mode**: the backend and website then run inside Linux containers, and nothing needs to be installed on Windows except Git, Python and Docker Desktop.

1. In `.env`, set `DEV_MODE=docker`.
2. Run `py dev.py setup`, then `py dev.py api`, and `py dev.py web` in a second terminal. The commands stay the same.
3. Extra Docker-mode commands: `py dev.py npm install <package>` (runs npm inside the container) and `py dev.py shell` (a terminal inside the backend container).

Code changes still reload automatically.
