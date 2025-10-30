# Technical Notes

This document provides technical implementation details for developers who want to understand or extend the Homepage application.

## Architecture Overview

### Technology Stack

- **Framework**: Flask 3.0+ (Python web microframework)
- **File Watching**: Watchdog 3.0+ (cross-platform file system events)
- **Configuration**: TOML (via tomllib/tomli)
- **Templating**: Jinja2 (built into Flask)
- **Service Management**: systemd user services

### Application Structure

```
Flask App
├── Routes
│   ├── / (index) - Main homepage with search bar
│   ├── /check_reload - Reload status endpoint
│   └── /wallpaper - Background image server
├── Client-Side Features
│   ├── Digital clock (JavaScript)
│   ├── Web search form (JavaScript)
│   └── Auto-reload checker (JavaScript)
├── File Watchers
│   ├── ~/.cache/wal/colors.json
│   └── ~/.wallpaper
└── Configuration Loaders
    ├── load_colors()
    ├── load_wallpaper()
    └── load_links()
```

## Key Design Decisions

### 1. Inline Assets

**Decision**: Embed CSS and JavaScript directly in the HTML template.

**Rationale**:
- Single HTTP request for initial page load
- No external asset management needed
- Simplified deployment (one Python file)
- Faster perceived performance
- No cache invalidation issues

**Trade-off**: Larger HTML file, but acceptable for a simple homepage.

### 2. Wallpaper HTTP Serving

**Decision**: Serve wallpaper via Flask endpoint instead of using `file://` URLs.

**Rationale**:
- Browsers block local `file://` URLs for security (CORS policy)
- HTTP serving is cross-browser compatible
- Allows dynamic wallpaper changes without code modification
- Transparent PNG fallback for missing wallpapers

**Implementation**:
```python
@app.route("/wallpaper")
def serve_wallpaper():
    wallpaper_path = load_wallpaper()
    if wallpaper_path:
        return send_file(wallpaper_path)
    # Return 1x1 transparent PNG
    return send_file(BytesIO(transparent_png), mimetype="image/png")
```

### 3. Client-Side Reload Checking

**Decision**: JavaScript polls `/check_reload` every 2 seconds instead of WebSockets.

**Rationale**:
- Simpler implementation (no WebSocket library needed)
- Lower server complexity
- 2-second delay acceptable for config changes
- Works with any reverse proxy
- No persistent connection overhead

**Trade-off**: Minimal extra HTTP requests vs. complexity.

### 4. Global State for File Watching

**Decision**: Use a module-level dictionary for reload state.

**Rationale**:
- Simplest thread-safe approach for boolean flag
- No need for database or caching layer
- Watchdog runs in separate thread
- Flask request handlers read the flag

**Implementation**:
```python
file_watcher_state = {"reload_needed": False}
```

### 5. Client-Side Search

**Decision**: Search is handled entirely in JavaScript on the client side.

**Rationale**:
- No server processing needed (lower load)
- Direct navigation to search provider
- Privacy-preserving (no queries logged server-side)
- Works even if server is temporarily unavailable
- Instant response (no round trip)

**Implementation**:
```javascript
function handleSearch(event) {
    const query = searchInput.value.trim();
    const searchUrls = {
        'brave': 'https://search.brave.com/search?q=',
        'google': 'https://www.google.com/search?q=',
        'duckduckgo': 'https://duckduckgo.com/?q=',
        'bing': 'https://www.bing.com/search?q='
    };
    window.open(searchUrls[provider] + encodeURIComponent(query));
}
```

**Trade-off**: No server-side search history or autocomplete, but better privacy.

### 6. TOML Configuration Format

**Decision**: Use TOML instead of JSON, YAML, or INI.

**Rationale**:
- Human-readable and editable
- Native Python support (tomllib in 3.11+)
- Supports hierarchical structures naturally
- Less verbose than JSON
- More structured than INI
- Simpler than YAML

## Implementation Details

### Color Scheme Loading

The application tries to load pywal colors and falls back to Gruvbox:

```python
def load_colors():
    if COLORS_FILE.exists():
        # Try to load pywal colors.json
        colors = json.load(...)
        # Extract special.background and special.foreground
        return colors
    # Fallback to hardcoded Gruvbox dark
    return GRUVBOX_DARK
```

**Key Points**:
- Pywal stores colors in `~/.cache/wal/colors.json`
- JSON contains `colors` dict (color0-15) and `special` dict (background, foreground)
- Gruvbox palette provides consistent fallback
- No error if pywal is not installed

### Wallpaper Path Resolution

```python
def load_wallpaper():
    if WALLPAPER_FILE.exists():
        wallpaper_path = read_file().strip()
        if Path(wallpaper_path).exists():
            return wallpaper_path
    return None
```

**Key Points**:
- `~/.wallpaper` is a plain text file with single path
- Path is validated before use
- Returns None if file missing or path invalid
- Flask route handles None gracefully

### File Watching Mechanism

Watchdog observes directories (not individual files) for changes:

```python
observer.schedule(handler, str(colors_dir), recursive=False)
observer.schedule(handler, str(wallpaper_dir), recursive=False)
```

**Why directories?**
- Files may be replaced atomically (new inode)
- Directory watching catches all modification methods
- Non-recursive for performance
- Filters by filename in event handler

### Template Rendering

Jinja2 template is defined as a string in Python:

```python
template = """<!DOCTYPE html>..."""
return render_template_string(template, colors=colors, ...)
```

**Benefits**:
- No separate template file needed
- All code in one file
- Easy to modify styles dynamically
- Direct variable interpolation

### Clock Implementation

JavaScript updates clock every second:

```javascript
function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    // ...
}
setInterval(updateClock, 1000);
```

**Key Points**:
- Uses browser's local time
- 24-hour format (0-23)
- Zero-padded for consistent width
- Updates date at midnight (60-second check interval)

### Search Implementation

Search form submits to client-side JavaScript handler:

```javascript
function handleSearch(event) {
    event.preventDefault();
    const query = searchInput.value.trim();
    const provider = searchProvider.value;
    // Open search results in new tab
    window.open(searchUrl, '_blank', 'noopener,noreferrer');
    searchInput.value = ''; // Clear input
}
```

**Search Providers**:
- **Brave Search** (default): `https://search.brave.com/search?q=`
- **Google**: `https://www.google.com/search?q=`
- **DuckDuckGo**: `https://duckduckgo.com/?q=`
- **Bing**: `https://www.bing.com/search?q=`

**Key Points**:
- URL encoding handles special characters
- New tab opens with security attributes
- Input clears after submission
- Provider persists across searches (dropdown state)
- Works without server interaction

## Performance Considerations

### Memory Usage

- **Template**: Compiled once, reused for each request
- **Configuration**: Loaded on each request (acceptable for low traffic)
- **File Watchers**: One thread per observer, minimal overhead
- **Flask**: Development server, single-threaded

### Optimization Opportunities

1. **Caching**: Cache TOML parsing results with file mtime check
2. **Production Server**: Use gunicorn/uwsgi for better concurrency
3. **Asset Optimization**: Minify inline CSS/JS
4. **Image Optimization**: Serve resized wallpaper for faster loading

### Current Performance Profile

- **Initial Load**: ~100-200ms (one HTTP request + wallpaper)
- **Reload Check**: ~10-20ms (lightweight JSON endpoint)
- **Memory**: ~40-60MB (Flask + Watchdog)
- **CPU**: <1% idle, <5% during reload

## Security Considerations

### Localhost-Only Binding

```python
app.run(host="127.0.0.1", port=5000)
```

**Why**: Prevents external network access to the homepage.

### Path Validation

All file paths are validated before use:
- Check file exists before serving
- Use Path objects for safe path handling
- No user input in file paths (config only)

### External Links

```html
<a href="..." target="_blank" rel="noopener noreferrer">
```

**Why**: Prevents reverse tabnabbing and referrer leakage.

### No Code Execution

- TOML config is data-only (no code)
- No eval() or exec() calls
- No template injection (controlled variables)

## Code Quality Standards

### Type Hints

All functions have type hints (implicit from docstrings):

```python
def load_colors() -> dict:
    """Load colors from pywal cache or use gruvbox dark fallback."""
```

### Linting Scores

- **Pylint**: 10.00/10
- **Ruff**: All checks passed
- **Pyright**: 0 errors, 0 warnings
- **Black**: Formatted to 100 char line length

### Testing Strategy

Currently manual testing. Future additions:
- Unit tests for color/wallpaper loading
- Integration tests for routes
- E2E tests with Selenium

## Extension Points

### Adding New Routes

```python
@app.route("/custom")
def custom_route():
    return jsonify({"status": "ok"})
```

### Custom Color Schemes

Modify `GRUVBOX_DARK` dictionary or add new fallback themes.

### Additional File Watchers

```python
if CUSTOM_FILE.exists():
    observer.schedule(handler, str(CUSTOM_FILE.parent))
```

### Template Customization

The template string can be:
- Split into separate file
- Generated dynamically
- Extended with Jinja2 inheritance

## Known Limitations

1. **Single Wallpaper**: Only one wallpaper at a time (no rotation)
2. **No Caching**: Config loaded on every request
3. **Dev Server**: Flask development server (not production-ready)
4. **No Link Search**: No search/filter functionality for configured links
5. **Static Icons**: Icons from TOML only (no dynamic icon loading)
6. **Client-Side Search**: Web search is client-side only (no server logging/autocomplete)

## Future Improvements

### Short Term

- [ ] Add wallpaper caching to reduce I/O
- [ ] Support wallpaper rotation (multiple files)
- [ ] Add search/filter functionality for links
- [ ] Support multiple color schemes (switchable)
- [ ] Add search suggestions/autocomplete
- [ ] Remember last used search provider

### Medium Term

- [ ] Add API for remote link management
- [ ] Browser extension for adding current tab
- [ ] Export/import link collections
- [ ] Dark/light mode toggle (independent of pywal)
- [ ] Search history tracking (optional, privacy-focused)
- [ ] Quick search keyboard shortcuts (e.g., / to focus search)

### Long Term

- [ ] Multi-user support with authentication
- [ ] Cloud sync for link configuration
- [ ] Mobile app for link management
- [ ] Analytics (most visited links)

## Debugging

### Enable Flask Debug Mode

```python
app.run(host="127.0.0.1", port=5000, debug=True)
```

**Warning**: Only for development, not production.

### Logging

Add logging to track behavior:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.debug("Wallpaper path: %s", wallpaper_path)
```

### Systemd Logs

```bash
journalctl --user -u homepage.service --since "5 minutes ago"
```

### Browser DevTools

- Network tab: Check `/wallpaper` response
- Console: View JavaScript errors
- Application: Check for reload polling

## Python Version Compatibility

### Version-Specific Code

```python
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
```

**Rationale**: `tomllib` added in Python 3.11, use `tomli` backport for 3.10.

### Supported Versions

- **Python 3.10**: Requires `tomli` package
- **Python 3.11+**: Uses built-in `tomllib`
- **Python 3.13+**: Should work (not tested)

## Build and Deployment

### Virtual Environment

Always use a virtual environment to avoid system package conflicts:

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### Systemd Service

The service file uses:
- `%h` = User home directory
- `Type=simple` = Foreground process
- `Restart=on-failure` = Auto-restart on crash

### Dependencies

**Production** (3 packages):
- flask >= 3.0.0
- watchdog >= 3.0.0
- tomli >= 2.0.1 (Python < 3.11 only)

**Development** (7 packages):
- All production packages
- black, ruff, pylint, pyright

## Contributing Guidelines

1. **Run quality checks**: `make check` before committing
2. **Maintain 10/10 pylint score**: No exceptions
3. **Add type hints**: For all new functions
4. **Update docs**: README, FEATURES, this file
5. **Test manually**: Run app and verify changes

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Watchdog Documentation](https://python-watchdog.readthedocs.io/)
- [pywal GitHub](https://github.com/dylanaraps/pywal)
- [TOML Specification](https://toml.io/)
- [systemd Service Files](https://www.freedesktop.org/software/systemd/man/systemd.service.html)