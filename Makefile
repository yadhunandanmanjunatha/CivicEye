# Shortcut for macOS/Linux. Every target just calls dev.py, which also works on Windows:
#   Windows:  py dev.py <command>
PYTHON ?= $(shell command -v python3.11 || command -v python3)

.PHONY: setup db migrate api web seed demo test llm-check reset full

setup db migrate api web seed test llm-check reset full:
	$(PYTHON) dev.py $@

demo: seed
	@cat docs/DEMO_SCRIPT.md 2>/dev/null || echo "docs/DEMO_SCRIPT.md not written yet"
