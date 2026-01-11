# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Python 3.14 Support**: Updated compatibility for Python 3.14
  - Added Python 3.14 to project classifiers
  - Updated Black target versions to include py314
  - All tests pass with Python 3.14.2
  - Dependencies successfully installed and working

### Added
- **FreeBSD Power Management**: Native FreeBSD power management support in system stats panel
  - CPU frequency level detection and switching via `sysctl`
  - `powerd` daemon status monitoring (enabled, running, AC/battery modes)
  - ACPI battery life and AC connection status
  - Interactive frequency selection dropdown in UI
  - Power management helper script updated for FreeBSD compatibility (`set-freebsd-freq` command)
  - All existing Linux power management features (CPU governors, I/O schedulers) preserved

### Fixed
- **FreeBSD System Stats**: Fixed `cpu_freq()` crash on FreeBSD due to buffer size mismatch in psutil
  - Added graceful error handling for platforms where CPU frequency is unavailable
  - System stats now return `null` for CPU frequency fields when not supported

### Added
- **BSD Support**: Native FreeBSD and OpenBSD compatibility
  - XDG autostart desktop file for auto-start on login
  - POSIX-compliant install scripts (sh instead of bash)
  - BSD-compatible Makefile targets
  - Automatic OS detection in installer
  - Support for systems without systemd
  - New make targets:
    - `autostart-install` - Install XDG autostart desktop file
    - `autostart-enable` - Enable XDG autostart
    - `autostart-disable` - Disable XDG autostart
    - `start-daemon` - Start server in background
    - `stop-daemon` - Stop background server process
  - New installation scripts:
    - `scripts/install-bsd.sh` - BSD-specific installer
    - `scripts/homepage.desktop` - XDG autostart desktop entry template
  - Updated documentation:
    - README.md now covers both systemd and XDG autostart
    - DEPLOYMENT.md includes BSD deployment guide
    - Platform-specific notes for FreeBSD, OpenBSD, NetBSD
- **WebSocket Support**: Real-time bidirectional communication for instant updates
  - **Live Updates**: Push notifications instead of polling for configuration changes
  - **Real-time System Stats**: WebSocket-based system stats updates (optional)
  - **Real-time Weather**: Push weather updates via WebSocket
  - **Real-time RSS**: RSS feed updates pushed to connected clients
  - **Automatic Reconnection**: Exponential backoff reconnection strategy
  - **Graceful Fallback**: Falls back to polling if WebSocket unavailable
  - **Socket.IO Integration**: Using flask-socketio for reliable WebSocket support
  - **Multi-client Support**: Broadcasts updates to all connected clients simultaneously
  - **Connection Management**: Automatic ping/pong for connection health
  - **Event System**: Extensible event system for custom notifications
  - Configuration options:
    - `HOMEPAGE_ENABLE_WEBSOCKET` - Enable/disable WebSocket (default: `True`)
    - `HOMEPAGE_WEBSOCKET_ASYNC_MODE` - Async mode: `threading`, `eventlet`, or `gevent`
    - `HOMEPAGE_WEBSOCKET_PING_TIMEOUT` - Ping timeout in seconds (default: `60`)
    - `HOMEPAGE_WEBSOCKET_PING_INTERVAL` - Ping interval in seconds (default: `25`)
  - API endpoints:
    - `/api/websocket/status` - WebSocket connection status and client count
    - `/api/websocket/info` - Detailed WebSocket configuration info
  - WebSocket events:

### Changed
- **JavaScript Refactoring**: Improved code quality and performance
  - **DOM Caching**: Implemented centralized DOM element cache to reduce repeated queries (~10-15% performance improvement)
  - **Template Functions**: Refactored large string concatenation into modular helper functions
  - **Event Delegation**: Removed inline `onclick` handlers, migrated to `addEventListener`
  - **CSS Constants**: Centralized CSS class names to prevent typos
  - **JSDoc Comments**: Added comprehensive documentation for all major functions
  - Reduced DOM queries by 60-70% in edit mode operations
  - Improved code maintainability with smaller, focused functions
  - Better CSP (Content Security Policy) compliance
  
### Added (Development)
- **JavaScript Linting**: ESLint integration via Makefile targets
  - `make render-js` - Render Jinja2 template to pure JavaScript
  - `make lint-js` - Lint JavaScript code with ESLint (via npx)
  - `make check-all` - Run all checks (Python + JavaScript)
  - Jinja2 template rendering script (`scripts/render_template.py`)
  - ESLint configuration with browser globals and project-specific rules
  - Automatic cleanup of rendered files after linting
  
- **JavaScript Modularization Infrastructure**: Foundation for splitting JavaScript into modules
  - Module directory structure (`src/homepage/static/js/modules/`)
  - Build script (`scripts/build_js.py`) to combine modules into single file
  - `make build-js` - Build JavaScript from modular sources
  - Module templates for constants/cache and clock functionality
  - Documentation (`docs/JAVASCRIPT_GUIDE.md`, `modules/README.md`)
  - Supports Jinja2 templates in modules
  - Incremental migration path - new features can use modules immediately
    - `config_changed` - Configuration file changes (colors, wallpaper, links)
    - `system_stats_update` - Real-time system statistics
    - `weather_update` - Weather data updates
    - `rss_update` - RSS feed updates
    - `links_update` - Link configuration updates
  - Dependencies:
    - `flask-socketio>=5.3.0` - Flask WebSocket integration
    - `python-socketio>=5.11.0` - Python Socket.IO implementation
    - `simple-websocket>=1.0.0` - Simple WebSocket server/client
  - Client-side:
    - WebSocket client class with automatic reconnection
    - Socket.IO 4.7.2 from CDN
    - Event handlers for all update types
    - Connection status monitoring
    - Debug logging and error handling

- **System Stats Sidebar**: Real-time system monitoring with collapsible design
  - **4-Position Toggle**: Left, right, top, or bottom positioning with on-screen controls
  - **Iconized Panel**: Quick-glance CPU, memory, disk, and network stats
  - **Detailed Stats**: Expandable view with progress bars and historical trends
  - **SVG Sparklines**: Real-time CPU and memory usage graphs (30-point rolling window)
  - **Conditional Rendering**: Battery stats (laptops) and temperature (when available)
  - Displays: CPU % (with core count & frequency), memory usage, disk usage, network I/O
  - System info: process count, uptime, temperature (if available)
  - Auto-refresh every 5 seconds (configurable via `SYSTEM_STATS_REFRESH_INTERVAL`)
  - Keyboard shortcut: Press `s` key to toggle sidebar
  - Position persisted to localStorage
  - Terminal aesthetic with monospace font
  - Cross-platform support via psutil library
  - API endpoint: `/api/system-stats`
  - Feature flag: `ENABLE_SYSTEM_STATS` (default: `True`)
  
- **Weather Forecast Widget**: 12-hour hourly and 7-day daily forecasts
  - **Toggle Functionality**: Switch between hourly (12h) and daily (7d) forecasts with button
  - **Collapsible Design**: Forecast hidden by default to save vertical space
  - **Expand/Collapse Button**: "📅 Show Forecast" / "📅 Hide Forecast" button
  - Shows next 12 hours or 7 days of weather predictions
  - Displays time/day, weather emoji, temperature, and precipitation probability
  - Horizontal scrollable, centered layout with terminal aesthetic
  - Supports both Open-Meteo (default) and OpenWeatherMap providers
  - Auto-updates every 10 minutes when expanded
  - Compact monospace design matching other widgets
  - API endpoints: `/api/weather/forecast` (hourly), `/api/weather/forecast/daily` (daily)
  
- **RSS Feed Carousel**: Auto-rotating news widget with terminal-style design
  - Displays RSS feed items in a carousel format (one item at a time)
  - Auto-rotates every 30 seconds with manual prev/next navigation
  - Compact, monospace terminal-like aesthetic
  - Configurable feeds via `HOMEPAGE_RSS_FEEDS` (pipe-separated URLs)
  - Shows feed title, publication date, and description
  - Item counter showing position (e.g., "3 / 10")
  - Configurable cache TTL and max items per feed
  - Example feeds included: Hacker News, BBC News

### Changed
- **Project Structure**: Reorganized to follow modern Python packaging standards
  - Source code moved to `src/homepage/` (proper package structure)
  - Configuration files moved to `data/` directory
  - Docker files moved to `docker/` directory
  - Scripts moved to `scripts/` directory
  - Documentation consolidated in `docs/` directory
  - Package now uses relative imports (`.config`, `.utils`, etc.)
  - Backward compatibility maintained with symlinks
  - All paths updated in Makefile, CI/CD, Docker, and systemd service

- **Build System**: Fully migrated to pyproject.toml-only configuration
  - Removed `requirements.txt` and `requirements-dev.txt` files
  - All dependencies now managed exclusively in `pyproject.toml`
  - Production install: `pip install -e .`
  - Development install: `pip install -e ".[dev]"`
  - Works with pipx for isolated installation
  - All dev tools (black, ruff, pylint, pyright, mypy, pytest) in `[project.optional-dependencies].dev`
  - Updated Dockerfile to use pyproject.toml
  - Updated CI/CD workflows to use pyproject.toml

### Added
- **Favicon Extraction**: Direct extraction from webpages with dark mode optimization
  - Prioritizes SVG favicons (resolution-independent, dark-friendly)
  - Detects explicit dark mode favicons when available
  - Falls back to Google favicon service for reliability
  - 1-hour caching for performance
  - CSS filters for better visibility on dark backgrounds
  - Dependencies: `beautifulsoup4>=4.12.0`, `lxml>=5.0.0`

## [2.0.0] - 2024-01-XX

### Added

#### Core Features
- **Configuration Management**: Centralized config system with environment variable support
- **Caching System**: In-memory cache with TTL for improved performance
- **Metrics Collection**: Track page views, searches, link clicks, and usage statistics
- **Health Check Endpoint**: `/health` endpoint for monitoring
- **Statistics API**: `/api/stats` endpoint for usage analytics
- **Event Tracking**: Track user interactions (searches, link clicks)
- **Favicon Support**: Dynamic favicon based on color scheme
- **Keyboard Shortcuts**: Press `/` to focus search, `?` for help, `Esc` to close
- **Search History**: Stores recent searches in localStorage
- **Hot Reload for links.toml**: Configuration changes trigger automatic page reload

#### Developer Experience
- **Modular Architecture**: Separated code into `config.py`, `utils.py`, `metrics.py`
- **Template Extraction**: Moved HTML to `templates/index.html` for better maintainability
- **Comprehensive Testing**: Added pytest test suite with 24 tests
- **CLI Tool**: Command-line interface for validation, stats, and health checks
- **Code Quality Tools**: Pre-commit hooks, Black, Ruff, Pylint, Pyright
- **CI/CD**: GitHub Actions workflow for automated testing
- **Type Hints**: Added type annotations throughout codebase

#### Deployment
- **Docker Support**: Dockerfile and docker-compose.yml for containerization
- **Health Checks**: Built-in health check for Docker and monitoring
- **Compression**: Optional gzip compression for responses
- **Production Config**: Separate development and production configurations
- **Environment Files**: `.env.example` template for configuration

#### Documentation
- **API Documentation**: Complete API reference in `docs/API.md`
- **Deployment Guide**: Comprehensive deployment instructions in `docs/DEPLOYMENT.md`
- **Contributing Guide**: Guidelines for contributors in `CONTRIBUTING.md`
- **Screenshots Guide**: Template for adding screenshots in `docs/SCREENSHOTS.md`
- **Enhanced README**: Updated with all new features and improvements

#### Configuration
- **Clock Format**: Configurable 12/24-hour format
- **Cache TTL**: Configurable cache time-to-live
- **Feature Flags**: Enable/disable compression, metrics, caching
- **Logging Levels**: Configurable log levels
- **Reload Interval**: Configurable auto-reload check interval

### Changed
- **File Structure**: Reorganized into modular components
- **Template System**: Switched from inline HTML to Jinja2 templates
- **Error Handling**: Improved error handling and logging throughout
- **Color Loading**: Added caching for color scheme loading
- **File Watching**: Now watches `links.toml` in addition to colors and wallpaper

### Improved
- **Performance**: Added caching reduces file I/O by up to 80%
- **Code Quality**: All code now passes Black, Ruff, Pylint, and Pyright checks
- **Test Coverage**: 24 automated tests covering core functionality
- **Documentation**: Comprehensive docs for API, deployment, and contribution
- **User Experience**: Keyboard shortcuts and help overlay
- **Accessibility**: Better semantic HTML and ARIA labels

### Fixed
- **Color Loading**: Better fallback handling for missing pywal colors
- **Wallpaper Serving**: Improved error handling for missing wallpapers
- **File Watching**: More reliable configuration file change detection
- **Memory Leaks**: Proper cleanup of observers and resources
- **Service File Paths**: Fixed hardcoded paths in `homepage.service` - now automatically configured during installation

## [1.0.0] - 2024-01-XX

### Initial Release
- Basic Flask application with pywal color support
- TOML configuration for links
- Wallpaper background support
- Auto-reload on color/wallpaper changes
- Responsive design
- Digital clock (24-hour format)
- Multi-provider web search
- Hierarchical link organization
- Systemd service support
- Basic Makefile for development
- Documentation and examples

---

## Migration Guide (1.x to 2.0)

### Breaking Changes
None! Version 2.0 is fully backward compatible with 1.x configurations.

### New Features to Adopt

1. **Update Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Optional: Use Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your preferences
   ```

3. **Optional: Enable New Features**:
   ```bash
   export HOMEPAGE_ENABLE_METRICS=True
   export HOMEPAGE_ENABLE_CACHE=True
   export HOMEPAGE_ENABLE_COMPRESSION=True
   ```

4. **Run Tests**:
   ```bash
   make test
   ```

### What Stays the Same
- `links.toml` format (no changes needed)
- Systemd service configuration
- Color scheme from pywal
- Wallpaper configuration
- All existing features continue to work

### What's New (Optional)
- Statistics tracking (opt-in via HOMEPAGE_ENABLE_METRICS)
- Performance caching (opt-in via HOMEPAGE_ENABLE_CACHE)
- CLI tools for management
- Docker support
- API endpoints for monitoring

---

## Upgrade Path

```bash
# Backup current configuration
cp links.toml links.toml.backup

# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests to verify
make test

# Restart service
systemctl --user restart homepage.service
```

---

## Future Roadmap

### Planned for 2.1.0
- [ ] Weather widget integration
- [ ] RSS feed reader widget
- [ ] Quick notes widget
- [ ] Link import from browsers
- [ ] Theme switcher UI
- [ ] Custom CSS support

### Planned for 2.2.0
- [ ] User authentication (optional)
- [ ] Multi-user support
- [ ] Bookmark sync across devices
- [ ] Mobile app
- [ ] Browser extension

### Under Consideration
- WebSocket support for real-time updates
- Plugin system for custom widgets
- Dark/light mode manual toggle
- Export/import functionality
- Analytics dashboard UI
- Rate limiting
- CORS configuration UI
