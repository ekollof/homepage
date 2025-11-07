"""Flask application for customizable homepage with dynamic theming."""

import logging
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_compress import Compress
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Load environment variables from .env file BEFORE importing config
load_dotenv()

from .config import get_config  # noqa: E402 # pylint: disable=wrong-import-position
from .metrics import MetricsCollector  # noqa: E402 # pylint: disable=wrong-import-position
from .utils import (  # noqa: E402 # pylint: disable=wrong-import-position
    SimpleCache,
    load_json_file,
    load_text_file,
    load_toml_file,
    merge_links_configs,
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

    __slots__ = ()

    def on_modified(self, event):
        """Mark that a reload is needed when files are modified."""
        if not event.is_directory:
            file_path = Path(str(event.src_path))
            match file_path.name:
                case "colors.json" | ".wallpaper" | "links.toml" | "links.override.toml":
                    logger.info("Configuration file changed: %s", file_path.name)
                    file_watcher_state["reload_needed"] = True
                    # Invalidate cache
                    if cache:
                        cache.clear()


def load_colors():
    """Load colors from pywal cache or use gruvbox dark fallback."""
    if cache and (cached := cache.get("colors")):
        return cached

    if colors_data := load_json_file(config.COLORS_FILE):
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
    if cache and (cached := cache.get("wallpaper")) is not None:
        return cached

    if wallpaper_text := load_text_file(config.WALLPAPER_FILE):
        wallpaper_path = Path(wallpaper_text)
        if wallpaper_path.exists():
            if cache:
                cache.set("wallpaper", str(wallpaper_path))
            return str(wallpaper_path)

    if cache:
        cache.set("wallpaper", None)
    return None


def load_links():
    """Load links from TOML configuration file.

    If override file exists, use it exclusively.
    Otherwise, use base configuration.
    """
    if cache and (cached := cache.get("links")):
        return cached

    # Load base configuration
    base_data = load_toml_file(config.CONFIG_FILE, {})

    # Load override configuration if it exists
    override_data = load_toml_file(config.CONFIG_OVERRIDE_FILE, {})

    # Use override if it exists, otherwise use base
    merged_data = merge_links_configs(base_data, override_data)
    categories = merged_data.get("category", [])

    if cache:
        cache.set("links", categories)
    return categories


# Import blueprints
from .routes import (  # noqa: E402 # pylint: disable=wrong-import-position
    api_bp,
    assets_bp,
    core_bp,
    editing_bp,
    init_api_blueprint,
    init_assets_blueprint,
    init_core_blueprint,
    init_editing_blueprint,
    init_rss_blueprint,
    init_system_stats_blueprint,
    init_weather_blueprint,
    rss_bp,
    system_stats_bp,
    weather_bp,
)

# Initialize and register blueprints
init_core_blueprint(load_colors, load_wallpaper, load_links, file_watcher_state, config)
app.register_blueprint(core_bp)

init_weather_blueprint(config)
app.register_blueprint(weather_bp)

init_system_stats_blueprint(config)
app.register_blueprint(system_stats_bp)

init_rss_blueprint(config, cache)
app.register_blueprint(rss_bp)

init_api_blueprint(metrics, config)
app.register_blueprint(api_bp)

init_editing_blueprint(config, cache, load_links, load_toml_file, file_watcher_state)
app.register_blueprint(editing_bp)

init_assets_blueprint(config, load_colors, load_wallpaper, render_template)
app.register_blueprint(assets_bp)


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
        logger.info("Watching directory: %s", colors_dir)

    # Watch wallpaper file directory
    wallpaper_dir = config.WALLPAPER_FILE.parent
    if wallpaper_dir.exists():
        file_observer.schedule(handler, str(wallpaper_dir), recursive=False)
        logger.info("Watching directory: %s", wallpaper_dir)

    # Watch links.toml directory
    links_dir = config.CONFIG_FILE.parent
    if links_dir.exists():
        file_observer.schedule(handler, str(links_dir), recursive=False)
        logger.info("Watching directory: %s", links_dir)

    file_observer.start()
    return file_observer


if __name__ == "__main__":
    logger.info("Starting Homepage application v2.0.0")
    logger.info("Host: %s, Port: %s", config.HOST, config.PORT)
    logger.info("Debug: %s", config.DEBUG)
    logger.info("Cache enabled: %s", config.ENABLE_CACHE)
    logger.info("Metrics enabled: %s", config.ENABLE_METRICS)
    logger.info("Compression enabled: %s", config.ENABLE_COMPRESSION)

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
            logger.info("Metrics exported to %s", metrics_file)
