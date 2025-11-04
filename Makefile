.PHONY: help install install-dev run clean lint format check test test-cov setup-hooks service-install service-start service-stop service-restart service-status service-enable service-disable logs docker-build docker-run docker-stop validate-config stats health export-metrics

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
BLACK = $(VENV)/bin/black
RUFF = $(VENV)/bin/ruff
PYLINT = $(VENV)/bin/pylint
PYRIGHT = $(VENV)/bin/pyright
PYTEST = $(VENV)/bin/pytest

help:
	@echo "Homepage Development Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install          - Create venv and install production dependencies"
	@echo "  install-dev      - Install development dependencies"
	@echo "  setup-hooks      - Install git pre-commit hooks"
	@echo "  run              - Run the application locally"
	@echo "  clean            - Remove virtual environment and cache files"
	@echo "  format           - Format code with black"
	@echo "  lint             - Run all linters (ruff, pylint, pyright)"
	@echo "  check            - Run format and lint checks"
	@echo "  test             - Run tests with pytest"
	@echo "  test-cov         - Run tests with coverage report"
	@echo "  validate-config  - Validate links.toml configuration"
	@echo "  stats            - Show application statistics"
	@echo "  health           - Check application health"
	@echo "  export-metrics   - Export metrics to JSON file"
	@echo "  docker-build     - Build Docker image"
	@echo "  docker-run       - Run Docker container"
	@echo "  docker-stop      - Stop Docker container"
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
	@echo "Installing package..."
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	@echo "Installation complete!"

install-dev: install
	@echo "Installing development dependencies..."
	$(PIP) install -e ".[dev]"
	@echo "Development dependencies installed!"

setup-hooks:
	@echo "Installing git pre-commit hooks..."
	@cp -f .githooks/pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "✅ Pre-commit hook installed!"
	@echo "   Hooks will run: black, ruff, pyright"
	@echo "   To skip hooks: git commit --no-verify"

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
	-$(PYLINT) app.py
	@echo "Running pyright..."
	$(PYRIGHT) app.py
	@echo "Linting complete!"

check: format lint
	@echo "All checks passed!"

test:
	@echo "Running tests..."
	$(PYTEST) tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	$(PYTEST) tests/ -v --cov=. --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/"

validate-config:
	@echo "Validating configuration..."
	$(PYTHON) cli.py validate

stats:
	@echo "Fetching application statistics..."
	$(PYTHON) cli.py stats

health:
	@echo "Checking application health..."
	$(PYTHON) cli.py health

export-metrics:
	@echo "Exporting metrics..."
	$(PYTHON) cli.py stats --export metrics_export.json

docker-build:
	@echo "Building Docker image..."
	docker build -t homepage:latest .

docker-run:
	@echo "Running Docker container..."
	docker-compose up -d

docker-stop:
	@echo "Stopping Docker container..."
	docker-compose down

service-install:
	@echo "Installing systemd service..."
	@mkdir -p ~/.config/systemd/user
	@sed "s|INSTALL_DIR_PLACEHOLDER|$(shell pwd)|g" homepage.service > ~/.config/systemd/user/homepage.service
	@systemctl --user daemon-reload
	@echo "Service installed to ~/.config/systemd/user/homepage.service"
	@echo "Working directory: $(shell pwd)"

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
