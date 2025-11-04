# Homepage AI Coding Agent Instructions

## Project Overview

Homepage is a Flask-based customizable startpage server that displays hierarchical links from TOML config with dynamic theming from pywal. The app serves a single-page interface with live wallpaper backgrounds, integrated search, and optional weather/metrics features.

**Key Architecture:**
- Single Flask app (`app.py`) with inline HTML template generation
- Configuration-driven theming (pywal colors → Gruvbox dark fallback)
- File watchers for hot-reload without server restart
- Optional metrics collection with in-memory state
- CLI tool for validation and monitoring (`cli.py`)

## Core Development Workflows

### Running and Testing

```bash
# Development setup (creates venv, installs deps, sets up systemd)
./install.sh

# Run locally (uses dev config, caching disabled)
make run
# OR direct: ./venv/bin/python app.py

# Run all code quality checks (black + ruff + pylint + pyright)
make check

# Run tests with coverage
make test-cov

# Validate links configuration
make validate-config
```

**Important:** The project uses a virtual environment at `./venv/`. All Python commands should use `./venv/bin/python` or use `make` targets.

### Systemd Service Management

The app is designed to run as a systemd user service:

```bash
make service-install    # Install service (auto-configured paths)
make service-start      # Start service
make logs              # Follow logs (journalctl)
```

Service file (`homepage.service`) uses placeholder `INSTALL_DIR_PLACEHOLDER` that gets replaced during installation.

## Configuration System

### Environment-Based Config (`config.py`)

The app uses a class-based config with environment variable overrides:

- `Config` - base class with defaults
- `DevelopmentConfig` - debug on, cache off
- `ProductionConfig` - debug off, cache on, secure secret key

**Environment Variables:**
- `HOMEPAGE_ENV` - `development` (default) or `production`
- `HOMEPAGE_HOST`, `HOMEPAGE_PORT` - server binding (default: `127.0.0.1:5000`)
- `HOMEPAGE_ENABLE_WEATHER`, `HOMEPAGE_ENABLE_METRICS` - feature flags
- `HOMEPAGE_ENABLE_EDITING` - enable/disable in-browser link editing (default: `True`)
- `HOMEPAGE_WEATHER_PROVIDER` - `openmeteo` (default, no API key) or `openweathermap`
- `HOMEPAGE_GEOIP_PROVIDER` - `maxmind` (default), `ipapi`, or `ip-api`

**Critical Paths:**
- `CONFIG_FILE = BASE_DIR / "links.toml"` - default link configuration
- `CONFIG_OVERRIDE_FILE = BASE_DIR / "links.override.toml"` - user edits (gitignored)
- `COLORS_FILE = Path.home() / ".cache/wal/colors.json"` - pywal colors
- `WALLPAPER_FILE = Path.home() / ".wallpaper"` - wallpaper path file

### Links Configuration (`links.toml`)

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

**Validation:** Use `cli.py validate` or `validate_links_config()` in `utils.py` to check structure before runtime.

### Configuration Override System (`links.override.toml`)

The app supports a simple two-file system:
- `links.toml` - base configuration (tracked in git)
- `links.override.toml` - user version (gitignored, auto-created on first edit)

**Override behavior** (see `merge_links_configs()` in `utils.py`):
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

All file loaders (`utils.py`) return defaults on error rather than raising exceptions:

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

### Caching Strategy (`SimpleCache` in `utils.py`)

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
- **Edit mode** (`ENABLE_EDITING=True`) - in-browser link editing:
  - Toggle with edit button (top-right) or `e` key
  - CRUD operations for categories, subcategories, and links
  - Saves to `links.override.toml` (gitignored)
  - Modal-based forms for adding/editing items
  - Confirmation dialogs for deletions

**No build step** - everything is inline for simplicity. Edit template in `app.py`.

## Common Pitfalls

1. **Don't import `config` directly in tests** - import `app` module and patch `app.config`
2. **File watchers need directories** - don't watch individual files
3. **Systemd service paths** - use `INSTALL_DIR_PLACEHOLDER` in service file, replaced by install script
4. **Weather location format** - must be `"lat,lon"` string (comma-separated floats)
5. **Cache invalidation** - file watchers call `cache.clear()` on change events
6. **Python 3.10 compatibility** - use `tomli` package, not `tomllib` directly

## Adding New Features

**Before adding new routes/features:**
1. Add feature flag in `Config` class with env var override
2. Add corresponding settings to both `DevelopmentConfig` and `ProductionConfig`
3. Check feature flag in route handler and return 404 if disabled
4. Add tests with monkeypatching to enable feature
5. Update CLI if feature needs monitoring/management

**Example pattern:**
```python
@app.route("/api/newfeature")
def new_feature():
    if not config.ENABLE_NEW_FEATURE:
        return jsonify({"error": "Feature not enabled"}), 404
    # ... implementation
```

---

*Generated from codebase analysis. Keep this file updated when architectural patterns change.*
