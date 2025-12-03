.PHONY: help install install-dev run clean lint format check test test-cov setup-hooks service-install service-start service-stop service-restart service-status service-enable service-disable logs autostart-install autostart-enable autostart-disable start-daemon stop-daemon docker-build docker-run docker-stop validate-config stats health export-metrics lint-js render-js check-all build-js

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
BLACK = $(VENV)/bin/black
RUFF = $(VENV)/bin/ruff
PYLINT = $(VENV)/bin/pylint
PYRIGHT = $(VENV)/bin/pyright
PYTEST = $(VENV)/bin/pytest
RENDER_SCRIPT = scripts/render_template.py
BUILD_JS_SCRIPT = scripts/build_js.py
RENDERED_JS = scripts_rendered.js
PWD != pwd

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
	@echo "  lint             - Run all linters (ruff, pyright)"
	@echo "  lint-js          - Lint JavaScript code with ESLint"
	@echo "  build-js         - Build JavaScript from modules"
	@echo "  render-js        - Render Jinja2 JavaScript template"
	@echo "  check            - Run format and lint checks (Python only)"
	@echo "  check-all        - Run all checks (Python + JavaScript)"
	@echo "  test             - Run tests with pytest"
	@echo "  test-cov         - Run tests with coverage report"
	@echo "  validate-config  - Validate links.toml configuration"
	@echo "  stats            - Show application statistics"
	@echo "  health           - Check application health"
	@echo "  export-metrics   - Export metrics to JSON file"
	@echo "  docker-build     - Build Docker image"
	@echo "  docker-run       - Run Docker container"
	@echo "  docker-stop      - Stop Docker container"
	@echo ""
	@echo "Linux with systemd:"
	@echo "  service-install  - Install systemd service"
	@echo "  service-start    - Start systemd service"
	@echo "  service-stop     - Stop systemd service"
	@echo "  service-restart  - Restart systemd service"
	@echo "  service-status   - Show systemd service status"
	@echo "  service-enable   - Enable systemd service auto-start"
	@echo "  service-disable  - Disable systemd service auto-start"
	@echo "  logs             - Follow systemd service logs"
	@echo ""
	@echo "BSD and other systems (XDG autostart):"
	@echo "  autostart-install - Install XDG autostart desktop file"
	@echo "  autostart-enable  - Enable XDG autostart"
	@echo "  autostart-disable - Disable XDG autostart"
	@echo "  start-daemon      - Start homepage in background"
	@echo "  stop-daemon       - Stop background homepage process"

install:
	@echo "Creating virtual environment..."
	@PYTHON_BIN=$$(sh scripts/find_python_interp.sh) && \
		$$PYTHON_BIN -m venv $(VENV) || \
		(echo "Error: Python 3.10+ not found" && exit 1)
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
	@echo "   Hooks will run: black, ruff (with --fix), pyright"
	@echo "   Same checks as CI pipeline"
	@echo "   To skip hooks: git commit --no-verify"

run:
	@echo "Starting homepage server on http://localhost:5000"
	$(PYTHON) -m homepage.app

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Cleanup complete!"

format:
	@echo "Formatting code with black..."
	$(BLACK) src/homepage/ tests/
	@echo "Formatting complete!"

lint:
	@echo "Running ruff..."
	$(RUFF) check src/homepage/ tests/
	@echo "Running pyright..."
	$(PYRIGHT) src/homepage/ tests/
	@echo "Linting complete!"

check: format lint
	@echo "All checks passed!"

check-all: format lint lint-js
	@echo "All checks passed (Python + JavaScript)!"

build-js:
	@echo "Building JavaScript from modules..."
	@$(PYTHON) $(BUILD_JS_SCRIPT)
	@echo "JavaScript build complete!"

render-js:
	@echo "Rendering Jinja2 JavaScript template..."
	@$(PYTHON) $(RENDER_SCRIPT) > $(RENDERED_JS)
	@echo "Rendered JavaScript to $(RENDERED_JS)"

lint-js: render-js
	@echo "Linting JavaScript with ESLint..."
	@npx eslint $(RENDERED_JS) --max-warnings 11
	@echo "JavaScript linting complete!"
	@rm -f $(RENDERED_JS)
	@echo "Cleaned up rendered file"

test:
	@echo "Running tests..."
	$(PYTEST) tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	$(PYTEST) tests/ -v --cov=. --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/"

validate-config:
	@echo "Validating configuration..."
	$(PYTHON) -m homepage.cli validate

stats:
	@echo "Fetching application statistics..."
	$(PYTHON) -m homepage.cli stats

health:
	@echo "Checking application health..."
	$(PYTHON) -m homepage.cli health

export-metrics:
	@echo "Exporting metrics..."
	$(PYTHON) -m homepage.cli stats --export metrics_export.json

docker-build:
	@echo "Building Docker image..."
	docker build -f docker/Dockerfile -t homepage:latest .

docker-run:
	@echo "Running Docker container..."
	docker-compose -f docker/docker-compose.yml up -d

docker-stop:
	@echo "Stopping Docker container..."
	docker-compose -f docker/docker-compose.yml down

service-install:
	@echo "Installing systemd service..."
	@mkdir -p ~/.config/systemd/user
	@sed "s|INSTALL_DIR_PLACEHOLDER|$(PWD)|g" scripts/homepage.service > ~/.config/systemd/user/homepage.service
	@systemctl --user daemon-reload
	@echo "Service installed to ~/.config/systemd/user/homepage.service"
	@echo "Working directory: $(PWD)"

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

# BSD/XDG Autostart targets
autostart-install:
	@echo "Installing XDG autostart desktop file..."
	@mkdir -p ~/.config/autostart
	@sed "s|INSTALL_DIR_PLACEHOLDER|$(PWD)|g" scripts/homepage.desktop > ~/.config/autostart/homepage.desktop
	@chmod +x ~/.config/autostart/homepage.desktop
	@echo "Desktop file installed to ~/.config/autostart/homepage.desktop"
	@echo "Working directory: $(PWD)"
	@echo "Autostart will activate on next login"

autostart-enable:
	@if [ -f ~/.config/autostart/homepage.desktop ]; then \
		sed -i.bak 's/Hidden=true/Hidden=false/' ~/.config/autostart/homepage.desktop && rm -f ~/.config/autostart/homepage.desktop.bak; \
		echo "Autostart enabled"; \
	else \
		echo "Error: Desktop file not found. Run 'make autostart-install' first."; \
		exit 1; \
	fi

autostart-disable:
	@if [ -f ~/.config/autostart/homepage.desktop ]; then \
		sed -i.bak 's/Hidden=false/Hidden=true/' ~/.config/autostart/homepage.desktop && rm -f ~/.config/autostart/homepage.desktop.bak; \
		echo "Autostart disabled"; \
	else \
		echo "Error: Desktop file not found."; \
		exit 1; \
	fi

start-daemon:
	@echo "Starting homepage in background..."
	@if pgrep -f "python.*homepage.app" > /dev/null; then \
		echo "Homepage is already running (PID: $$(pgrep -f 'python.*homepage.app'))"; \
	else \
		nohup $(PYTHON) -m homepage.app > /tmp/homepage.log 2>&1 & \
		echo "Homepage started (PID: $$!)"; \
		echo "Logs: /tmp/homepage.log"; \
	fi

stop-daemon:
	@echo "Stopping homepage..."
	@if pgrep -f "python.*homepage.app" > /dev/null; then \
		pkill -f "python.*homepage.app" && echo "Homepage stopped" || echo "Failed to stop homepage"; \
	else \
		echo "Homepage is not running"; \
	fi
