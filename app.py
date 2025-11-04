"""Flask application for customizable homepage with dynamic theming."""

import base64
import logging
from io import BytesIO
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from flask_compress import Compress
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config import get_config
from metrics import MetricsCollector
from utils import (
    SimpleCache,
    load_json_file,
    load_text_file,
    load_toml_file,
)

# Initialize configuration
config = get_config()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)

# Enable compression if configured
if config.ENABLE_COMPRESSION:
    Compress(app)

# Initialize metrics collector if enabled
metrics = MetricsCollector() if config.ENABLE_METRICS else None

# Initialize cache if enabled
cache = SimpleCache(ttl=config.CACHE_TTL) if config.ENABLE_CACHE else None

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global state for file modification tracking
file_watcher_state = {"reload_needed": False}


class ConfigFileHandler(FileSystemEventHandler):
    """Handler for file system events on config files."""

    def on_modified(self, event):
        """Mark that a reload is needed when files are modified."""
        if not event.is_directory:
            file_path = Path(str(event.src_path))
            if file_path.name in ("colors.json", ".wallpaper", "links.toml"):
                logger.info(f"Configuration file changed: {file_path.name}")
                file_watcher_state["reload_needed"] = True
                # Invalidate cache
                if cache:
                    cache.clear()


def load_colors():
    """Load colors from pywal cache or use gruvbox dark fallback."""
    if cache:
        cached = cache.get("colors")
        if cached:
            return cached

    colors_data = load_json_file(config.COLORS_FILE)
    if colors_data:
        try:
            colors = colors_data.get("colors", {})
            colors["background"] = colors_data.get("special", {}).get(
                "background", colors.get("color0", config.GRUVBOX_DARK["background"])
            )
            colors["foreground"] = colors_data.get("special", {}).get(
                "foreground", colors.get("color7", config.GRUVBOX_DARK["foreground"])
            )
            if cache:
                cache.set("colors", colors)
            return colors
        except KeyError:
            pass

    if cache:
        cache.set("colors", config.GRUVBOX_DARK)
    return config.GRUVBOX_DARK


def load_wallpaper():
    """Load wallpaper path or return None."""
    if cache:
        cached = cache.get("wallpaper")
        if cached is not None:
            return cached

    wallpaper_text = load_text_file(config.WALLPAPER_FILE)
    if wallpaper_text:
        wallpaper_path = Path(wallpaper_text)
        if wallpaper_path.exists():
            if cache:
                cache.set("wallpaper", str(wallpaper_path))
            return str(wallpaper_path)

    if cache:
        cache.set("wallpaper", None)
    return None


def load_links():
    """Load links from TOML configuration file."""
    if cache:
        cached = cache.get("links")
        if cached:
            return cached

    toml_data = load_toml_file(config.CONFIG_FILE, {})
    categories = toml_data.get("category", [])

    if cache:
        cache.set("links", categories)
    return categories


@app.before_request
def before_request():
    """Track request metrics."""
    if metrics:
        metrics.track_request(request.path)


@app.route("/")
def index():
    """Render the homepage."""
    colors = load_colors()
    wallpaper = load_wallpaper()
    categories = load_links()

    return render_template(
        "index.html",
        colors=colors,
        wallpaper=wallpaper,
        categories=categories,
        clock_format=config.CLOCK_FORMAT,
        reload_interval=config.RELOAD_CHECK_INTERVAL,
    )


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "uptime": metrics.get_uptime() if metrics else 0,
            "version": "2.0.0",
        }
    )


@app.route("/api/stats")
def stats():
    """Get application statistics."""
    if not metrics:
        return jsonify({"error": "Metrics not enabled"}), 404

    return jsonify(metrics.get_stats())


@app.route("/api/track", methods=["POST"])
def track():
    """Track user events."""
    if not metrics:
        return jsonify({"status": "disabled"}), 200

    try:
        data = request.get_json()
        event_type = data.get("event")
        event_data = data.get("data", {})

        if event_type == "search":
            metrics.track_search(event_data.get("provider", "unknown"), event_data.get("query", ""))
        elif event_type == "link_click":
            metrics.track_link_click(event_data.get("name", "unknown"), event_data.get("url", ""))

        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        return jsonify({"status": "error"}), 500


@app.route("/check_reload")
def check_reload():
    """Check if a reload is needed due to file changes."""
    reload = file_watcher_state["reload_needed"]
    if reload:
        file_watcher_state["reload_needed"] = False
    return jsonify({"reload": reload})


@app.route("/wallpaper")
def serve_wallpaper():
    """Serve the wallpaper image."""
    wallpaper_path = load_wallpaper()
    if wallpaper_path:
        try:
            return send_file(wallpaper_path)
        except (OSError, FileNotFoundError):
            logger.warning(f"Wallpaper file not found: {wallpaper_path}")
    # Return a 1x1 transparent PNG if no wallpaper
    transparent_png = base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
        b"AAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    return send_file(BytesIO(transparent_png), mimetype="image/png")


@app.route("/favicon")
def favicon():
    """Serve favicon."""
    # Generate a simple favicon based on first color
    colors = load_colors()
    color4 = colors.get("color4", "#458588")
    fg_color = colors.get("foreground", "#ebdbb2")
    # Create a 16x16 colored square as favicon
    favicon_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
        <rect width="16" height="16" fill="{color4}"/>
        <text x="8" y="12" font-size="10" text-anchor="middle" fill="{fg_color}">H</text>
    </svg>"""
    return favicon_svg, 200, {"Content-Type": "image/svg+xml"}


def start_file_watcher():
    """Start watching configuration files for changes."""
    if not config.WATCH_FILES:
        logger.info("File watching disabled")
        return None

    file_observer = Observer()
    handler = ConfigFileHandler()

    # Watch colors.json directory
    colors_dir = config.COLORS_FILE.parent
    if colors_dir.exists():
        file_observer.schedule(handler, str(colors_dir), recursive=False)
        logger.info(f"Watching directory: {colors_dir}")

    # Watch wallpaper file directory
    wallpaper_dir = config.WALLPAPER_FILE.parent
    if wallpaper_dir.exists():
        file_observer.schedule(handler, str(wallpaper_dir), recursive=False)
        logger.info(f"Watching directory: {wallpaper_dir}")

    # Watch links.toml directory
    links_dir = config.CONFIG_FILE.parent
    if links_dir.exists():
        file_observer.schedule(handler, str(links_dir), recursive=False)
        logger.info(f"Watching directory: {links_dir}")

    file_observer.start()
    return file_observer


if __name__ == "__main__":
    logger.info("Starting Homepage application v2.0.0")
    logger.info(f"Host: {config.HOST}, Port: {config.PORT}")
    logger.info(f"Debug: {config.DEBUG}")
    logger.info(f"Cache enabled: {config.ENABLE_CACHE}")
    logger.info(f"Metrics enabled: {config.ENABLE_METRICS}")
    logger.info(f"Compression enabled: {config.ENABLE_COMPRESSION}")

    observer = start_file_watcher()
    try:
        app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
    finally:
        if observer:
            observer.stop()
            observer.join()
        if metrics:
            # Export metrics on shutdown
            metrics_file = Path("metrics.json")
            metrics.export_to_file(metrics_file)
            logger.info(f"Metrics exported to {metrics_file}")
