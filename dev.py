#!/usr/bin/env python3
"""CivicFlow developer commands. Works the same on Windows, macOS and Linux.

    Windows:      py dev.py <command>        (or: python dev.py <command>)
    macOS/Linux:  python3 dev.py <command>   (or: make <command>)

Commands:
    setup      create .env, Python virtual env, install backend + web dependencies
    db         start the PostGIS database in Docker (port 5433)
    migrate    start db + apply database migrations
    api        start db + migrate + run the backend on http://localhost:8000 (auto-reload)
    web        run the website on http://localhost:5173
    seed       start db + migrate + load starting data (idempotent)
    test       run backend tests (+ e2e tests if they exist)
    llm-check  check which configured LLM providers work
    reset      delete the database volume (ALL data)
    full       run everything in Docker (for judges)
    shell      (Docker mode) open a terminal inside the backend container
    npm ...    (Docker mode) run npm inside the web container, e.g. `dev.py npm install leaflet`

Docker mode: put DEV_MODE=docker in .env. The backend and website then run inside Linux
containers (needed on Windows laptops whose security policy blocks Python/Node native files).
Commands stay the same.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
WEB = ROOT / "web"
VENV = BACKEND / ".venv"
WINDOWS = os.name == "nt"
VENV_PY = VENV / ("Scripts/python.exe" if WINDOWS else "bin/python")


def env_value(key: str, default: str = "") -> str:
    """Read a setting from the process environment, then from .env."""
    if key in os.environ:
        return os.environ[key]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(key + "="):
                return line.split("=", 1)[1].split("#", 1)[0].strip()
    return default


def docker_mode() -> bool:
    return env_value("DEV_MODE", "local").lower() == "docker"


def compose(*args: str, check: bool = True) -> int:
    return run([tool("docker"), "compose", "--profile", "dev", *args], check=check)


def in_api(*cmd: str) -> None:
    """Run a command inside a fresh backend container (source mounted, database reachable)."""
    db()
    compose("run", "--rm", "--build", "api-dev", *cmd)


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True) -> int:
    print(f"\n> {' '.join(str(c) for c in cmd)}", flush=True)
    try:
        return subprocess.run(cmd, cwd=cwd, check=check).returncode
    except FileNotFoundError:
        sys.exit(f"Command not found: {cmd[0]}. Is it installed and on your PATH?")
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        return 130


def tool(name: str) -> str:
    """Resolve npm/npx/docker to their real executable (npm is npm.cmd on Windows)."""
    path = shutil.which(name)
    if not path:
        hints = {"docker": "Install Docker Desktop and make sure it is running.",
                 "npm": "Install Node.js 20+ from nodejs.org.", "npx": "Install Node.js 20+ from nodejs.org."}
        sys.exit(f"'{name}' was not found. {hints.get(name, '')}")
    return path


def need_venv() -> None:
    if not VENV_PY.exists():
        sys.exit("Python environment not found. Run the 'setup' command first.")


def setup() -> None:
    if sys.version_info < (3, 11):
        sys.exit(f"Python 3.11+ is required, but this is {sys.version.split()[0]}. "
                 "Windows: install 3.11 from python.org and run `py -3.11 dev.py setup`.")
    env, example = ROOT / ".env", ROOT / ".env.example"
    if not env.exists():
        shutil.copy(example, env)
        print("Created .env from .env.example. Open it and fill in the empty values.")
    if docker_mode():
        db()
        compose("build", "api-dev")
        compose("pull", "web-dev", check=False)
        print("\nSetup complete (Docker mode). Next: `dev.py api`, then `dev.py web` in a 2nd terminal.")
        return
    if not VENV_PY.exists():
        run([sys.executable, "-m", "venv", str(VENV)])
    run([str(VENV_PY), "-m", "pip", "install", "-q", "--upgrade", "pip"])
    run([str(VENV_PY), "-m", "pip", "install", "-q", "-e", f"{BACKEND}[dev]"])
    if (WEB / "package.json").exists():
        run([tool("npm"), "install"], cwd=WEB)
    print("\nSetup complete.")


def db() -> None:
    docker = tool("docker")
    if run([docker, "info"], check=False) != 0:
        sys.exit("Docker is installed but not running. Open Docker Desktop, wait until it says "
                 "'Engine running', then try again.")
    run([docker, "compose", "up", "-d", "--wait", "db"])


def migrate() -> None:
    if docker_mode():
        return in_api("alembic", "upgrade", "head")
    need_venv()
    db()
    run([str(VENV_PY), "-m", "alembic", "upgrade", "head"], cwd=BACKEND)


def api() -> None:
    if docker_mode():
        db()
        compose("up", "--build", "api-dev", check=False)
        return
    migrate()
    run([str(VENV_PY), "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000", "--workers", "1"],
        cwd=BACKEND, check=False)


def web() -> None:
    if docker_mode():
        if not (WEB / "package.json").exists():
            sys.exit("web/ has no package.json yet (Lane B task B01).")
        compose("up", "web-dev", check=False)
        return
    if not (WEB / "package.json").exists():
        sys.exit("web/ has no package.json yet (Lane B task B01).")
    if not (WEB / "node_modules").exists():
        run([tool("npm"), "install"], cwd=WEB)
    run([tool("npm"), "run", "dev"], cwd=WEB, check=False)


def seed() -> None:
    if docker_mode():
        return in_api("sh", "-c", "alembic upgrade head && python -m app.seed")
    migrate()
    run([str(VENV_PY), "-m", "app.seed"], cwd=BACKEND)


def test() -> None:
    if docker_mode():
        in_api("python", "-m", "pytest", *sys.argv[2:])
        if (ROOT / "e2e" / "package.json").exists():
            print("e2e tests: run them on the Mac (Lane A) or in CI.")
        return
    need_venv()
    db()
    run([str(VENV_PY), "-m", "pytest"], cwd=BACKEND)
    if (ROOT / "e2e" / "package.json").exists():
        run([tool("npx"), "playwright", "test"], cwd=ROOT / "e2e")


def llm_check() -> None:
    if docker_mode():
        return in_api("python", "-m", "scripts.llm_check")
    need_venv()
    run([str(VENV_PY), "-m", "scripts.llm_check"], cwd=BACKEND)


def reset() -> None:
    run([tool("docker"), "compose", "down", "-v"])


def shell() -> None:
    in_api("bash")


def npm(args: list[str]) -> None:
    """Run npm in the web container (Docker mode) or on the laptop (local mode)."""
    if docker_mode():
        compose("run", "--rm", "--no-deps", "web-dev", "npm", *args)
    else:
        run([tool("npm"), *args], cwd=WEB)


def full() -> None:
    run([tool("docker"), "compose", "--profile", "full", "up", "--build"], check=False)


COMMANDS = {"setup": setup, "db": db, "migrate": migrate, "api": api, "web": web, "seed": seed,
            "test": test, "llm-check": llm_check, "reset": reset, "full": full, "shell": shell}

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "npm":
        npm(sys.argv[2:])
    elif len(sys.argv) >= 2 and sys.argv[1] in COMMANDS and (len(sys.argv) == 2 or sys.argv[1] == "test"):
        COMMANDS[sys.argv[1]]()
    else:
        print(__doc__)
        sys.exit(1)
