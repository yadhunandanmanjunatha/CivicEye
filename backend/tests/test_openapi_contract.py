"""Fails when an endpoint is added/removed without updating the contract snapshot.
If the change is intended: regenerate tests/openapi_paths.txt and follow the contract rule in CLAUDE.md."""
from pathlib import Path

from app.main import create_app

SNAPSHOT = Path(__file__).with_name("openapi_paths.txt")


def test_paths_match_contract_snapshot():
    spec = create_app().openapi()
    current = sorted(f"{m.upper()} {p}" for p, ops in spec["paths"].items() for m in ops)
    assert current == SNAPSHOT.read_text().split("\n")[:-1]
