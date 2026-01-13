# Homepage AI Coding Agent Instructions

## Project Overview

Homepage is a Flask-based customizable startpage server that displays hierarchical links from TOML config with dynamic theming from pywal. The app serves a single-page interface with live wallpaper backgrounds, integrated search, and optional weather/metrics features.

**Key Architecture:**
- Modern Python package structure in `src/homepage/` with modular route/service separation
- Flask app (`src/homepage/app.py`) with Jinja2 template generation
- Configuration-driven theming (pywal colors → Gruvbox dark fallback)
- File watchers for hot-reload without server restart
- Optional features: metrics, weather, RSS feeds, system stats, WebSocket support
- CLI tool for validation and monitoring (`src/homepage/cli.py`)

**Project Structure:**
```
homepage/
├── src/homepage/          # Python package source code
│   ├── app.py            # Main Flask application (registers blueprints)
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration management
│   ├── metrics.py        # Metrics collection
│   ├── utils.py          # Utility functions
│   ├── routes/           # Route blueprints (modular)
│   │   ├── api.py        # Metrics/tracking API
│   │   ├── assets.py     # Static asset routes
│   │   ├── core.py       # Main page routes
│   │   ├── editing.py    # Link editing endpoints
│   │   ├── rss.py        # RSS feed endpoints
│   │   ├── system_stats.py # System statistics
│   │   ├── weather.py    # Weather endpoints
│   │   └── websocket.py  # WebSocket routes
│   ├── services/         # Business logic layer
│   │   ├── geoip_service.py        # GeoIP location detection
│   │   ├── rss_service.py          # RSS feed fetching
│   │   ├── system_stats_service.py # System metrics
│   │   ├── weather_service.py      # Weather data
│   │   └── websocket_service.py    # WebSocket real-time updates
│   ├── templates/        # Jinja2 templates
│   └── static/           # Static assets
│       └── js/modules/   # JavaScript modules (13 files)
├── data/                  # Configuration and data files
│   ├── links.toml        # Link configuration (base, tracked)
│   ├── links.override.toml # User edits (gitignored)
│   └── *.mmdb            # GeoIP databases
├── docker/                # Docker configuration
├── scripts/               # Installation and build scripts
├── docs/                  # Comprehensive documentation (20+ files)
└── tests/                 # Test suite
```

## Modular Architecture

### Route Blueprints (`src/homepage/routes/`)

The application uses Flask blueprints for route organization:

- **`core.py`** - Main page rendering (`/`, `/check_reload`)
- **`api.py`** - Metrics and tracking endpoints (`/api/track`, `/api/metrics`)
- **`weather.py`** - Weather data endpoint (`/api/weather`)
- **`rss.py`** - RSS feed endpoint (`/api/rss`)
- **`system_stats.py`** - System statistics endpoint (`/api/system-stats`)
- **`editing.py`** - Link configuration editing (`/api/links/*`)
- **`assets.py`** - Static asset serving (wallpaper, favicon)
- **`websocket.py`** - WebSocket connection handler (`/ws`)

All blueprints are registered in `src/homepage/app.py` via `app.register_blueprint()`.

### Service Layer (`src/homepage/services/`)

Business logic is separated into service modules:

- **`weather_service.py`** - Weather data fetching (OpenMeteo, OpenWeatherMap)
- **`geoip_service.py`** - IP geolocation (MaxMind, ipapi, ip-api)
- **`rss_service.py`** - RSS feed parsing and caching
- **`system_stats_service.py`** - System metrics (CPU, memory, disk, network)
- **`websocket_service.py`** - WebSocket connection management and broadcasting

Services are imported by route handlers and provide clean separation of concerns.

## Core Development Workflows

### JavaScript Module System

**CRITICAL:** JavaScript files are modular and must be built before changes take effect.

The JavaScript is organized in modules located in `src/homepage/static/js/modules/` (13 total):
- `01-constants-and-cache.js.j2` - DOM cache and constants
- `02-clock.js.j2` - Clock functionality
- `03-weather.js.j2` - Weather widget
- `04-rss.js.j2` - RSS feed widget
- `05-search.js.j2` - Search functionality
- `06-system-stats.js.j2` - System stats widget
- `07-collapsible-stats.js.j2` - Collapsible system stats panel
- `08-edit-mode-core.js.j2` - Edit mode core logic
- `09-edit-templates.js.j2` - HTML generation for edit mode
- `10-edit-modals.js.j2` - Modal dialogs for editing
- `11-drag-drop.js.j2` - Drag and drop functionality
- `12-collapsible-categories.js.j2` - Collapsible category sections
- `13-initialization.js.j2` - Page initialization

**Workflow for JavaScript changes:**
```bash
# 1. Edit module files in src/homepage/static/js/modules/
# 2. Build combined JavaScript file
make build-js

# 3. Restart service to pick up changes
make service-restart

# 4. Verify changes are rendered
curl -s http://localhost:5000/ | grep "your-change"
```

**Important Notes:**
- `src/homepage/templates/scripts.js.j2` is GENERATED - do not edit directly
- `make render-js` is only for linting, not for deployment
- Flask renders templates at runtime, no separate render step needed
- Service restart may fail if port is in use - kill stale processes first: `pkill -f "python.*homepage"`

### Running and Testing

```bash
# Development setup (creates venv, installs deps, sets up autostart)
# Auto-detects: systemd (Linux) or XDG autostart (BSD)
./scripts/install.sh

# Run locally (uses dev config, caching disabled)
make run
# OR direct: ./venv/bin/python -m homepage.app

# Run all code quality checks (black + ruff + pylint + pyright)
make check

# Run tests with coverage
make test-cov

# Validate links configuration
make validate-config
```

**Important:** The project uses a virtual environment at `./venv/`. All Python commands should use `./venv/bin/python` or use `make` targets.

### Service Management

The app supports multiple service/autostart systems:

**Linux with systemd:**
```bash
make service-install    # Install systemd user service (auto-configured paths)
make service-start      # Start service
make service-stop       # Stop service
make logs              # Follow logs (journalctl)
```

Service file (`scripts/homepage.service`) uses placeholder `INSTALL_DIR_PLACEHOLDER` that gets replaced during installation.

**BSD and XDG Autostart (FreeBSD, OpenBSD, NetBSD, Linux without systemd):**
```bash
make autostart-install  # Install XDG autostart desktop file
make start-daemon      # Start in background (or wait for next login)
make stop-daemon       # Stop background process
# Logs: /tmp/homepage.log
```

Desktop file (`scripts/homepage.desktop`) uses placeholder `INSTALL_DIR_PLACEHOLDER` that gets replaced during installation. Auto-starts on login via XDG autostart mechanism.

**Platform Detection:**
The `install.sh` script automatically detects the OS and chooses the appropriate method:
- FreeBSD, OpenBSD, NetBSD, DragonFly → XDG autostart
- Linux with systemd → systemd user service
- Linux without systemd → XDG autostart

## Configuration System

### Environment-Based Config (`src/homepage/config.py`)

The app uses a class-based config with environment variable overrides:

- `Config` - base class with defaults
- `DevelopmentConfig` - debug on, cache off
- `ProductionConfig` - debug off, cache on, secure secret key

**Environment Variables:**
- `HOMEPAGE_ENV` - `development` (default) or `production`
- `HOMEPAGE_HOST`, `HOMEPAGE_PORT` - server binding (default: `127.0.0.1:5000`)
- `HOMEPAGE_DEBUG` - enable Flask debug mode (default: `False`)
- `HOMEPAGE_SECRET_KEY` - Flask secret key for sessions
- `HOMEPAGE_ENABLE_CACHE` - enable response caching (default: `True`, disabled in dev)
- `HOMEPAGE_ENABLE_COMPRESSION` - enable gzip compression (default: `True`)
- `HOMEPAGE_ENABLE_METRICS` - enable metrics collection (default: `True`)
- `HOMEPAGE_ENABLE_WEATHER` - enable weather widget (default: `False`)
- `HOMEPAGE_ENABLE_RSS` - enable RSS feed widget (default: `False`)
- `HOMEPAGE_ENABLE_EDITING` - enable in-browser link editing (default: `True`)
- `HOMEPAGE_ENABLE_SYSTEM_STATS` - enable system stats widget (default: `True`)
- `HOMEPAGE_ENABLE_WEBSOCKET` - enable WebSocket real-time updates (default: `True`)
- `HOMEPAGE_WEATHER_PROVIDER` - `openmeteo` (default, no API key) or `openweathermap`
- `HOMEPAGE_WEATHER_API_KEY` - API key for OpenWeatherMap
- `HOMEPAGE_WEATHER_LOCATION` - manual location override (`lat,lon` or city name)
- `HOMEPAGE_WEATHER_UNITS` - `metric` (default) or `imperial`
- `HOMEPAGE_GEOIP_PROVIDER` - `maxmind` (default), `ipapi`, or `ip-api`
- `HOMEPAGE_GEOIP_DB_PATH` - path to MaxMind GeoLite2 database
- `HOMEPAGE_CLOCK_FORMAT` - `24` (default) or `12`
- `HOMEPAGE_RSS_FEEDS` - pipe-separated list of RSS feed URLs
- `HOMEPAGE_RSS_MAX_ITEMS` - max items per feed (default: `5`)
- `HOMEPAGE_RSS_CACHE_TTL` - RSS cache TTL in seconds (default: `300`)
- `HOMEPAGE_SYSTEM_STATS_REFRESH_INTERVAL` - refresh interval in seconds (default: `5`)
- `HOMEPAGE_SYSTEM_STATS_POSITION` - widget position: `left`, `right`, `top`, or `bottom` (default: `left`)
- `HOMEPAGE_WEBSOCKET_PING_TIMEOUT` - WebSocket ping timeout (default: `60`)
- `HOMEPAGE_WEBSOCKET_PING_INTERVAL` - WebSocket ping interval (default: `25`)
- `HOMEPAGE_LOG_LEVEL` - logging level (default: `INFO`)

**Critical Paths:**
- `BASE_DIR = Path(__file__).parent.parent.parent` - Project root
- `DATA_DIR = BASE_DIR / "data"` - Data directory
- `CONFIG_FILE = DATA_DIR / "links.toml"` - default link configuration
- `CONFIG_OVERRIDE_FILE = DATA_DIR / "links.override.toml"` - user edits (gitignored)
- `COLORS_FILE = Path.home() / ".cache/wal/colors.json"` - pywal colors
- `WALLPAPER_FILE = Path.home() / ".wallpaper"` - wallpaper path file

### Links Configuration (`data/links.toml`)

Hierarchical structure with 3 levels:
```toml
[[category]]
name = "Development"
icon = "💻"
  [[category.links]]           # Direct link
  name = "GitHub"
  url = "https://github.com"
  icon = "🔗"
  
  [[category.subcategory]]     # Subcategory with nested links
  name = "Documentation"
  icon = "📚"
    [[category.subcategory.links]]
    name = "Python Docs"
    url = "https://docs.python.org"
```

**Validation:** Use `python -m homepage.cli validate` or `validate_links_config()` in `src/homepage/utils.py` to check structure before runtime.

### Configuration Override System (`data/links.override.toml`)

The app supports a simple two-file system:
- `data/links.toml` - base configuration (tracked in git)
- `data/links.override.toml` - user version (gitignored, auto-created on first edit)

**Override behavior** (see `merge_links_configs()` in `src/homepage/utils.py`):
- If override exists, use it **exclusively** (base ignored)
- If override doesn't exist, use base
- First edit: base automatically copied to override
- Allows full control including deletions
- Reset: just delete override file

## Critical Patterns

### Python Version Compatibility (3.10+)

The project targets Python 3.10+ and uses modern patterns:
- Match statements (`match/case`) instead of if/elif chains
- TOML parsing with `tomllib` (3.11+) or `tomli` (3.10 backport)
- `__slots__` for performance-critical classes
- Walrus operator (`:=`) for cleaner conditionals

**Example from codebase:**
```python
# Pattern: Match statement for provider selection
match config.WEATHER_PROVIDER:
    case "openmeteo":
        weather_data = _fetch_openmeteo_weather(lat, lon)
    case "openweathermap":
        weather_data = _fetch_openweathermap_weather(lat, lon)
```

### File Loading with Graceful Fallbacks

All file loaders (`src/homepage/utils.py`) return defaults on error rather than raising exceptions:

```python
# Pattern: Safe loading with walrus + early return
if colors_data := load_json_file(config.COLORS_FILE):
    try:
        colors = colors_data.get("colors", {})
        # ... process colors
    except KeyError:
        pass
return config.GRUVBOX_DARK  # Fallback always
```

**Never let missing config files crash the app** - pywal colors, wallpaper, and links all have fallbacks.

### Caching Strategy (`SimpleCache` in `src/homepage/utils.py`)

In-memory TTL cache for expensive operations (file I/O, color parsing):

```python
# Pattern: Check cache before expensive operation
if cache and (cached := cache.get("colors")):
    return cached

# Do expensive work...
if cache:
    cache.set("colors", colors)
```

Cache is **disabled in development** (`DevelopmentConfig.ENABLE_CACHE = False`) but **enabled in production**. File watchers invalidate cache on change.

### File Watching for Hot Reload

`ConfigFileHandler` watches directories (not files) for changes to `colors.json`, `.wallpaper`, and `links.toml`. Sets global flag `file_watcher_state["reload_needed"]` which frontend polls via `/check_reload`.

**Important:** Watch parent directories, not individual files, because editors often replace files on save.

## Testing Conventions

Tests in `tests/test_app.py` use pytest with fixtures:

- `app` fixture - Flask test app
- `client` fixture - Flask test client
- Monkeypatching for config/env vars
- Mock `requests.get` for external API tests
- Weather tests verify error handling (connection, timeout, missing DB)

**Pattern: Testing environment-dependent features**
```python
def test_weather_with_config(client, monkeypatch):
    import app as app_module
    monkeypatch.setattr(app_module.config, "ENABLE_WEATHER", True)
    monkeypatch.setattr(app_module.config, "WEATHER_LOCATION", "52.0,5.0")
    # ... test
```

Always patch `app_module.config` (not `config` module) because Flask app imports at module level.

## Tooling and Code Quality

### Development Tools (`pyproject.toml` config)

- **Black** - formatting (line length 100)
- **Ruff** - fast linting (pycodestyle, pyflakes, isort, bugbear)
- **Pylint** - additional static analysis
- **Pyright** - type checking (basic mode, tolerates missing imports)
- **pytest** - testing with coverage

**Run before commit:** `make check` (formats then lints)

### CLI Tool Usage (`cli.py`)

The CLI uses argparse subcommands and is designed for monitoring running services:

```bash
./venv/bin/python cli.py validate --check-urls  # Validate + HTTP check all links
./venv/bin/python cli.py stats                   # Fetch live stats from running app
./venv/bin/python cli.py health                  # Health check
./venv/bin/python cli.py export -o config.json  # Export TOML to JSON
```

CLI commands expect the Flask app to be running for `stats` and `health` endpoints.

## Weather and GeoIP Features

### Weather Provider Selection

Two providers with different requirements:
- **Open-Meteo** (default) - free, no API key, uses WMO weather codes
- **OpenWeatherMap** - requires API key in `HOMEPAGE_WEATHER_API_KEY`

### GeoIP Location Detection

Three providers for IP → location:
- **MaxMind GeoLite2** (default) - local database file (`GeoLite2-City.mmdb`), must be downloaded separately
- **ipapi.co** - free tier 30k req/month
- **ip-api.com** - free tier 45 req/minute

**Pattern:** Manual location (`lat,lon` in config) bypasses GeoIP. Localhost requests get fallback handling.

## RSS Feed Features

RSS feed widget displays aggregated feeds from multiple sources:
- Configured via `HOMEPAGE_RSS_FEEDS` (pipe-separated URLs)
- Cached with configurable TTL (`HOMEPAGE_RSS_CACHE_TTL`, default 5 minutes)
- Max items per feed limit (`HOMEPAGE_RSS_MAX_ITEMS`, default 5)
- Fetched via `/api/rss` endpoint
- Service handles parsing, validation, and error handling

## System Stats Features

Real-time system metrics widget with configurable positioning:
- **Metrics collected:** CPU usage, memory usage, disk usage, network I/O, uptime
- **Position:** `HOMEPAGE_SYSTEM_STATS_POSITION` - `left` (default), `right`, `top`, or `bottom`
- **Refresh interval:** `HOMEPAGE_SYSTEM_STATS_REFRESH_INTERVAL` (default 5 seconds)
- **Collapsible panel:** Can be expanded/collapsed to save screen space
- **WebSocket updates:** Real-time push updates when WebSocket enabled
- Platform-specific implementation (works on Linux, BSD, macOS, Windows)

## WebSocket Features

Real-time bidirectional communication for live updates:
- **Enabled by default:** `HOMEPAGE_ENABLE_WEBSOCKET=True`
- **Async mode:** Threading (dev), eventlet/gevent (production recommended)
- **Broadcasts:** Config changes, system stats updates, weather updates
- **Connection management:** Automatic reconnection, ping/pong heartbeat
- **Configuration:**
  - `HOMEPAGE_WEBSOCKET_PING_TIMEOUT` - timeout in seconds (default 60)
  - `HOMEPAGE_WEBSOCKET_PING_INTERVAL` - ping interval (default 25)
  - `HOMEPAGE_WEBSOCKET_ASYNC_MODE` - threading, eventlet, or gevent

## Metrics System (`metrics.py`)

In-memory metrics with thread-safe counters:
- Request counts, page views, search events, link clicks
- Top links by click count
- Search provider breakdown
- Recent events queue (max 1000, FIFO)

**Lifecycle:** Metrics export to `metrics.json` on shutdown. Frontend tracks events with `/api/track` endpoint.

## Frontend Integration

Template (`templates/index.html`) is Flask-rendered with inline CSS/JS:
- Clock updates every second (24h or 12h format via config)
- Polls `/check_reload` every 2s for config changes
- Posts search/click events to `/api/track` when metrics enabled
- Fetches weather from `/api/weather` on load if enabled
- Fetches RSS feeds from `/api/rss` if enabled
- Displays system stats from `/api/system-stats` if enabled
- **WebSocket support** (`ENABLE_WEBSOCKET=True`) - real-time updates for stats, weather, and config changes
- **Edit mode** (`ENABLE_EDITING=True`) - in-browser link editing:
  - Toggle with edit button (top-right) or `e` key
  - CRUD operations for categories, subcategories, and links
  - Saves to `links.override.toml` (gitignored)
  - Modal-based forms for adding/editing items
  - Confirmation dialogs for deletions
- **Collapsible UI** - categories and stats panels can be collapsed/expanded

**No build step** - everything is inline for simplicity. Edit template in `app.py`.

## Common Pitfalls

1. **Don't import modules directly in tests** - use `homepage.app`, `homepage.config`, etc.
2. **Use relative imports in package** - `.config`, `.utils`, `.metrics` within `src/homepage/`
3. **File watchers need directories** - don't watch individual files
4. **Systemd service paths** - use `INSTALL_DIR_PLACEHOLDER` in service file, replaced by install script
5. **Weather location format** - must be `"lat,lon"` string (comma-separated floats)
6. **Cache invalidation** - file watchers call `cache.clear()` on change events
7. **Python 3.10 compatibility** - use `tomli` package, not `tomllib` directly
8. **Configuration files** - always reference `data/` directory for config files
9. **WebSocket threading** - use `threading` mode for development, consider `eventlet`/`gevent` for production
10. **Route registration** - all routes are in blueprints registered in `app.py`, not in app.py directly

## Adding New Features

**Before adding new routes/features:**
1. Add feature flag in `Config` class in `src/homepage/config.py` with env var override
2. Add corresponding settings to both `DevelopmentConfig` and `ProductionConfig`
3. Create appropriate route module in `src/homepage/routes/` and/or service in `src/homepage/services/`
4. Register blueprint in `src/homepage/app.py` (don't add routes directly to app.py)
5. Check feature flag in route handler and return 404 if disabled
6. Add tests with monkeypatching to enable feature
7. Update CLI if feature needs monitoring/management
8. Document in `docs/FEATURES.md` and update `docs/API.md` if adding endpoints

**Example pattern:**
```python
# src/homepage/routes/newfeature.py
from flask import Blueprint, jsonify
from ..config import get_config

config = get_config()
newfeature_bp = Blueprint("newfeature", __name__)

@newfeature_bp.route("/api/newfeature")
def new_feature():
    if not config.ENABLE_NEW_FEATURE:
        return jsonify({"error": "Feature not enabled"}), 404
    # ... implementation
```

**Then register in app.py:**
```python
from .routes.newfeature import newfeature_bp
app.register_blueprint(newfeature_bp)
```

## Documentation Guidelines

**Important:** Do NOT create summary markdown files to document changes. The git changelog (`CHANGELOG.md`) is the single source of truth for project changes.

- Update `CHANGELOG.md` with all changes following Keep a Changelog format
- Keep only `README.md` and `CHANGELOG.md` in the project root
- All other documentation belongs in `docs/` directory (20+ specialized guides available)
- Use git commit messages for detailed change history
- Summary documents are redundant and add maintenance burden

**Available documentation in `docs/`:**
- `API.md` - REST API and WebSocket endpoint documentation
- `FEATURES.md` - Feature overview and configuration
- `TECHNICAL.md` - Technical architecture details
- `JAVASCRIPT_GUIDE.md` - JavaScript module system guide
- `EDITING.md` - In-browser editing feature
- `WEBSOCKET.md` - WebSocket implementation details
- `DEPLOYMENT.md` - Production deployment guide
- `BSD_INSTALL.md` - BSD-specific installation
- `MIGRATION.md` - Version migration guides
- `GEOIP_SETUP.md` - GeoIP database setup
- `POWER_MANAGEMENT_SETUP.md` - Power management configuration
- And more (see `docs/` directory)

---

*Generated from codebase analysis. Keep this file updated when architectural patterns change.*
