"""Configuration management for Homepage application."""

import os
from pathlib import Path


class Config:
    """Application configuration class."""

    # Flask settings
    HOST = os.getenv("HOMEPAGE_HOST", "127.0.0.1")
    PORT = int(os.getenv("HOMEPAGE_PORT", "5000"))
    DEBUG = os.getenv("HOMEPAGE_DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("HOMEPAGE_SECRET_KEY", "dev-secret-key-change-in-production")

    # File paths
    BASE_DIR = Path(__file__).parent
    CONFIG_FILE = BASE_DIR / "links.toml"
    CONFIG_OVERRIDE_FILE = BASE_DIR / "links.override.toml"
    COLORS_FILE = Path.home() / ".cache" / "wal" / "colors.json"
    WALLPAPER_FILE = Path.home() / ".wallpaper"

    # Cache settings
    CACHE_TTL = int(os.getenv("HOMEPAGE_CACHE_TTL", "5"))  # seconds
    ENABLE_CACHE = os.getenv("HOMEPAGE_ENABLE_CACHE", "True").lower() == "true"

    # Auto-reload settings
    RELOAD_CHECK_INTERVAL = int(os.getenv("HOMEPAGE_RELOAD_INTERVAL", "2000"))  # milliseconds
    WATCH_FILES = os.getenv("HOMEPAGE_WATCH_FILES", "True").lower() == "true"

    # Feature flags
    ENABLE_COMPRESSION = os.getenv("HOMEPAGE_ENABLE_COMPRESSION", "True").lower() == "true"
    ENABLE_METRICS = os.getenv("HOMEPAGE_ENABLE_METRICS", "True").lower() == "true"
    ENABLE_WEATHER = os.getenv("HOMEPAGE_ENABLE_WEATHER", "False").lower() == "true"
    ENABLE_RSS = os.getenv("HOMEPAGE_ENABLE_RSS", "False").lower() == "true"
    ENABLE_EDITING = os.getenv("HOMEPAGE_ENABLE_EDITING", "True").lower() == "true"

    # Weather settings (optional)
    WEATHER_PROVIDER = os.getenv(
        "HOMEPAGE_WEATHER_PROVIDER", "openmeteo"
    )  # openmeteo or openweathermap
    WEATHER_API_KEY = os.getenv("HOMEPAGE_WEATHER_API_KEY", "")  # Only needed for openweathermap
    WEATHER_LOCATION = os.getenv("HOMEPAGE_WEATHER_LOCATION", "")  # Optional: lat,lon or city name
    WEATHER_UNITS = os.getenv("HOMEPAGE_WEATHER_UNITS", "metric")  # metric or imperial
    GEOIP_PROVIDER = os.getenv("HOMEPAGE_GEOIP_PROVIDER", "maxmind")  # maxmind, ipapi, or ip-api
    GEOIP_DB_PATH = os.getenv(
        "HOMEPAGE_GEOIP_DB_PATH", str(Path(__file__).parent / "GeoLite2-City.mmdb")
    )

    # Clock settings
    CLOCK_FORMAT = os.getenv("HOMEPAGE_CLOCK_FORMAT", "24")  # 24 or 12

    # Logging
    LOG_LEVEL = os.getenv("HOMEPAGE_LOG_LEVEL", "INFO")

    # Gruvbox dark theme fallback colors
    GRUVBOX_DARK = {
        "background": "#282828",
        "foreground": "#ebdbb2",
        "color0": "#282828",
        "color1": "#cc241d",
        "color2": "#98971a",
        "color3": "#d79921",
        "color4": "#458588",
        "color5": "#b16286",
        "color6": "#689d6a",
        "color7": "#a89984",
        "color8": "#928374",
        "color9": "#fb4934",
        "color10": "#b8bb26",
        "color11": "#fabd2f",
        "color12": "#83a598",
        "color13": "#d3869b",
        "color14": "#8ec07c",
        "color15": "#ebdbb2",
    }


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    ENABLE_CACHE = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SECRET_KEY = os.getenv("HOMEPAGE_SECRET_KEY", os.urandom(24).hex())


def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv("HOMEPAGE_ENV", "development").lower()
    match env:
        case "production":
            return ProductionConfig()
        case _:
            return DevelopmentConfig()
