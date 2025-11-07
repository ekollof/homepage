"""Flask blueprint routes for Homepage application."""

from .api import api_bp, init_api_blueprint
from .assets import assets_bp, init_assets_blueprint
from .core import core_bp, init_core_blueprint
from .editing import editing_bp, init_editing_blueprint
from .rss import init_rss_blueprint, rss_bp
from .system_stats import init_system_stats_blueprint, system_stats_bp
from .weather import init_weather_blueprint, weather_bp
from .websocket import init_websocket_blueprint, websocket_bp

__all__ = [
    "core_bp",
    "init_core_blueprint",
    "api_bp",
    "init_api_blueprint",
    "weather_bp",
    "init_weather_blueprint",
    "system_stats_bp",
    "init_system_stats_blueprint",
    "rss_bp",
    "init_rss_blueprint",
    "editing_bp",
    "init_editing_blueprint",
    "assets_bp",
    "init_assets_blueprint",
    "websocket_bp",
    "init_websocket_blueprint",
]
