.PHONY: help install install-dev run clean lint format check test service-install service-start service-stop service-restart service-status service-enable service-disable logs

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
BLACK = $(VENV)/bin/black
RUFF = $(VENV)/bin/ruff
PYLINT = $(VENV)/bin/pylint
PYRIGHT = $(VENV)/bin/pyright

help:
	@echo "Homepage Development Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install          - Create venv and install production dependencies"
	@echo "  install-dev      - Install development dependencies"
	@echo "  run              - Run the application locally"
	@echo "  clean            - Remove virtual environment and cache files"
	@echo "  format           - Format code with black"
	@echo "  lint             - Run all linters (ruff, pylint, pyright)"
	@echo "  check            - Run format and lint checks"
	@echo "  service-install  - Install systemd service"
	@echo "  service-start    - Start systemd service"
	@echo "  service-stop     - Stop systemd service"
	@echo "  service-restart  - Restart systemd service"
	@echo "  service-status   - Show systemd service status"
	@echo "  service-enable   - Enable systemd service auto-start"
	@echo "  service-disable  - Disable systemd service auto-start"
	@echo "  logs             - Follow systemd service logs"

install:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Installation complete!"

install-dev: install
	@echo "Installing development dependencies..."
	$(PIP) install -r requirements-dev.txt
	@echo "Development dependencies installed!"

run:
	@echo "Starting homepage server on http://localhost:5000"
	$(PYTHON) app.py

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Cleanup complete!"

format:
	@echo "Formatting code with black..."
	$(BLACK) app.py
	@echo "Formatting complete!"

lint:
	@echo "Running ruff..."
	$(RUFF) check app.py
	@echo "Running pylint..."
	$(PYLINT) app.py
	@echo "Running pyright..."
	$(PYRIGHT) app.py
	@echo "All linters passed!"

check: format lint
	@echo "All checks passed!"

service-install:
	@echo "Installing systemd service..."
	mkdir -p ~/.config/systemd/user
	cp homepage.service ~/.config/systemd/user/
	systemctl --user daemon-reload
	@echo "Service installed!"

service-start:
	systemctl --user start homepage.service
	@echo "Service started!"

service-stop:
	systemctl --user stop homepage.service
	@echo "Service stopped!"

service-restart:
	systemctl --user restart homepage.service
	@echo "Service restarted!"

service-status:
	systemctl --user status homepage.service

service-enable:
	systemctl --user enable homepage.service
	@echo "Service enabled for auto-start!"

service-disable:
	systemctl --user disable homepage.service
	@echo "Service disabled from auto-start!"

logs:
	journalctl --user -u homepage.service -f
