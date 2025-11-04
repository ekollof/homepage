"""Flask application for customizable homepage with dynamic theming."""

import base64
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import tomli_w
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, render_template, request, send_file
from flask_compress import Compress
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Load environment variables from .env file BEFORE importing config
load_dotenv()

from config import get_config  # noqa: E402 # pylint: disable=wrong-import-position
from metrics import MetricsCollector  # noqa: E402 # pylint: disable=wrong-import-position
from utils import (  # noqa: E402 # pylint: disable=wrong-import-position
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

    response = make_response(
        render_template(
            "index.html",
            colors=colors,
            wallpaper=wallpaper,
            categories=categories,
            clock_format=config.CLOCK_FORMAT,
            reload_interval=config.RELOAD_CHECK_INTERVAL,
            config=config,
        )
    )

    # Prevent caching when editing is enabled
    if config.ENABLE_EDITING:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


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

        match event_type:
            case "search":
                metrics.track_search(
                    event_data.get("provider", "unknown"), event_data.get("query", "")
                )
            case "link_click":
                metrics.track_link_click(
                    event_data.get("name", "unknown"), event_data.get("url", "")
                )

        return jsonify({"status": "ok"})
    except (KeyError, ValueError, TypeError) as e:
        logger.error("Error tracking event: %s", e)
        return jsonify({"status": "error"}), 500


@app.route("/api/weather")
def get_weather():  # pylint: disable=too-many-return-statements
    """Get weather data using configured provider."""
    if not config.ENABLE_WEATHER:
        return jsonify({"error": "Weather feature not enabled"}), 404

    try:
        # Get location
        lat, lon, location_name = _get_location()

        # Get weather data based on provider
        match config.WEATHER_PROVIDER:
            case "openmeteo":
                weather_data = _fetch_openmeteo_weather(lat, lon)
            case "openweathermap":
                if not config.WEATHER_API_KEY:
                    return jsonify({"error": "OpenWeatherMap API key required"}), 400
                weather_data = _fetch_openweathermap_weather(lat, lon)
            case _:
                return jsonify({"error": "Invalid weather provider"}), 400

        weather_data["location"] = location_name
        return jsonify(weather_data)

    except requests.ConnectionError:
        logger.warning("Weather: No network connection available")
        return jsonify({"error": "No network connection"}), 503
    except requests.Timeout:
        logger.warning("Weather: Request timed out")
        return jsonify({"error": "Request timed out"}), 504
    except (requests.RequestException, KeyError, ValueError) as e:
        logger.error("Error fetching weather: %s", e)
        return jsonify({"error": "Weather service unavailable"}), 503


def _get_location() -> tuple[float, float, str]:
    """Get location from config or GeoIP."""
    # Check if location is provided in config
    if config.WEATHER_LOCATION:
        # Parse lat,lon format
        if "," in config.WEATHER_LOCATION:
            try:
                lat, lon = map(float, config.WEATHER_LOCATION.split(","))
                return lat, lon, f"{lat:.2f},{lon:.2f}"
            except ValueError:
                pass

    # Use GeoIP to determine location
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if client_ip and client_ip != "127.0.0.1":
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = None

    match config.GEOIP_PROVIDER:
        case "maxmind":
            return _geoip_maxmind(client_ip)
        case "ipapi":
            # Use ipapi.co (30k requests/month free)
            url = f"https://ipapi.co/{client_ip + '/' if client_ip else ''}json/"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data["latitude"], data["longitude"], data.get("city", "Unknown")
        case _:
            # ip-api provider (45 requests/minute free)
            url = f"http://ip-api.com/json/{client_ip if client_ip else ''}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data["status"] == "success":
                return data["lat"], data["lon"], data.get("city", "Unknown")

    raise ValueError("Could not determine location")


def _geoip_maxmind(ip_address: str | None) -> tuple[float, float, str]:
    """Get location using MaxMind GeoLite2 database."""
    import geoip2.database  # pylint: disable=import-outside-toplevel
    import geoip2.errors  # pylint: disable=import-outside-toplevel

    db_path = Path(config.GEOIP_DB_PATH)
    if not db_path.exists():
        raise FileNotFoundError(
            f"MaxMind database not found at {db_path}. "
            "Download from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data"
        )

    # Use a default IP if localhost
    if not ip_address:
        # Fallback: try to get public IP or use a default location
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=3)
            ip_address = response.json()["ip"]
        except (requests.RequestException, KeyError):
            # Ultimate fallback to a central location
            return 52.0, 5.0, "Netherlands"

    with geoip2.database.Reader(str(db_path)) as reader:
        try:
            # ip_address is guaranteed to be str here due to fallback above
            assert ip_address is not None
            response = reader.city(ip_address)
            city = response.city.name or "Unknown"
            lat = response.location.latitude or 0.0
            lon = response.location.longitude or 0.0
            return lat, lon, city
        except geoip2.errors.AddressNotFoundError as err:
            raise ValueError(f"IP address {ip_address} not found in GeoIP database") from err


def _fetch_openmeteo_weather(lat: float, lon: float) -> dict[str, Any]:
    """Fetch weather from Open-Meteo (no API key needed)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "temperature_unit": "celsius" if config.WEATHER_UNITS == "metric" else "fahrenheit",
        "wind_speed_unit": "kmh" if config.WEATHER_UNITS == "metric" else "mph",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    current = data["current"]

    # Map WMO weather codes to descriptions
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Foggy",
        51: "Light drizzle",
        53: "Drizzle",
        55: "Heavy drizzle",
        61: "Light rain",
        63: "Rain",
        65: "Heavy rain",
        71: "Light snow",
        73: "Snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Light showers",
        81: "Showers",
        82: "Heavy showers",
        85: "Light snow showers",
        86: "Snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with hail",
    }

    return {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "description": weather_codes.get(current["weather_code"], "Unknown"),
        "wind_speed": current["wind_speed_10m"],
        "units": config.WEATHER_UNITS,
    }


def _fetch_openweathermap_weather(lat: float, lon: float) -> dict[str, Any]:
    """Fetch weather from OpenWeatherMap (requires API key)."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": config.WEATHER_API_KEY,
        "units": config.WEATHER_UNITS,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"].title(),
        "wind_speed": data["wind"]["speed"],
        "units": config.WEATHER_UNITS,
    }


@app.route("/check_reload")
def check_reload():
    """Check if a reload is needed due to file changes."""
    reload = file_watcher_state["reload_needed"]
    if reload:
        file_watcher_state["reload_needed"] = False
    return jsonify({"reload": reload})


@app.route("/api/config")
def get_config_data():
    """Get current links configuration.

    On first access, copies base to override if override doesn't exist.
    This allows editing without modifying the base file.
    """
    if not config.ENABLE_EDITING:
        return jsonify({"error": "Editing not enabled"}), 404

    # Copy base to override if override doesn't exist
    if not config.CONFIG_OVERRIDE_FILE.exists():
        base_data = load_toml_file(config.CONFIG_FILE, {})
        if base_data:
            try:
                with open(config.CONFIG_OVERRIDE_FILE, "wb") as f:
                    tomli_w.dump(base_data, f)

                logger.info("Created override file from base configuration")

                # Invalidate cache
                if cache:
                    cache.clear()
            except (OSError, ValueError) as e:
                logger.error("Failed to create override file: %s", e)
                return jsonify({"error": "Failed to initialize override file"}), 500

    categories = load_links()
    return jsonify({"category": categories})


@app.route("/api/config", methods=["POST"])
def save_config_data():
    """Save links configuration to override file."""
    if not config.ENABLE_EDITING:
        return jsonify({"error": "Editing not enabled"}), 404

    try:
        data = request.get_json()
        if not data or "category" not in data:
            return jsonify({"error": "Invalid configuration data"}), 400

        # Validate the configuration
        from utils import validate_links_config  # pylint: disable=import-outside-toplevel

        valid, errors = validate_links_config(data)
        if not valid:
            return jsonify({"error": "Invalid configuration", "details": errors}), 400

        # Write to override file using tomli_w (already imported at top)

        with open(config.CONFIG_OVERRIDE_FILE, "wb") as f:
            tomli_w.dump(data, f)
            f.flush()  # Ensure data is written to disk
            os.fsync(f.fileno())  # Force OS to write to disk

        # Invalidate cache
        if cache:
            cache.clear()

        # Set reload flag for file watcher
        file_watcher_state["reload_needed"] = True

        logger.info("Configuration saved to override file")
        return jsonify({"status": "ok"})

    except (ValueError, TypeError, OSError) as e:
        logger.error("Error saving configuration: %s", e)
        return jsonify({"error": "Failed to save configuration"}), 500


@app.route("/api/config/reset", methods=["POST"])
def reset_config():
    """Reset configuration by removing override file."""
    if not config.ENABLE_EDITING:
        return jsonify({"error": "Editing not enabled"}), 404

    try:
        if config.CONFIG_OVERRIDE_FILE.exists():
            config.CONFIG_OVERRIDE_FILE.unlink()
            logger.info("Override configuration deleted")

        # Invalidate cache
        if cache:
            cache.clear()

        return jsonify({"status": "ok"})

    except OSError as e:
        logger.error("Error deleting override file: %s", e)
        return jsonify({"error": "Failed to reset configuration"}), 500


@app.route("/api/favicon")
def get_favicon_proxy():
    """Proxy favicon requests to avoid CORS issues.

    Fetches favicon from Google's service and returns as base64 data URI.
    """
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter required"}), 400

    try:
        # Extract domain from URL
        parsed = urlparse(url)
        domain = parsed.hostname or parsed.path

        # Fetch favicon from Google's service
        favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
        response = requests.get(favicon_url, timeout=5)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch favicon"}), 404

        # Convert to base64 data URI
        content_type = response.headers.get("Content-Type", "image/png")
        favicon_base64 = base64.b64encode(response.content).decode("utf-8")
        data_uri = f"data:{content_type};base64,{favicon_base64}"

        return jsonify({"favicon": data_uri})

    except (requests.RequestException, ValueError) as e:
        logger.error("Error fetching favicon: %s", e)
        return jsonify({"error": "Failed to fetch favicon"}), 500


@app.route("/wallpaper")
def serve_wallpaper():
    """Serve the wallpaper image."""
    wallpaper_path = load_wallpaper()
    if wallpaper_path:
        try:
            return send_file(wallpaper_path)
        except (OSError, FileNotFoundError):
            logger.warning("Wallpaper file not found: %s", wallpaper_path)
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
