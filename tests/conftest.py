"""Pytest configuration and fixtures."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_colors():
    """Sample color scheme data."""
    return {
        "special": {"background": "#282828", "foreground": "#ebdbb2"},
        "colors": {
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
        },
    }


@pytest.fixture
def sample_links():
    """Sample links configuration."""
    return {
        "category": [
            {
                "name": "Development",
                "icon": "💻",
                "links": [
                    {
                        "name": "GitHub",
                        "url": "https://github.com",
                        "icon": "🔗",
                    },
                    {
                        "name": "GitLab",
                        "url": "https://gitlab.com",
                        "icon": "🔗",
                    },
                ],
                "subcategory": [
                    {
                        "name": "Documentation",
                        "icon": "📚",
                        "links": [
                            {
                                "name": "Python Docs",
                                "url": "https://docs.python.org",
                                "icon": "🐍",
                            }
                        ],
                    }
                ],
            }
        ]
    }


@pytest.fixture
def colors_file(temp_dir, sample_colors):
    """Create a temporary colors.json file."""
    colors_file = temp_dir / "colors.json"
    with open(colors_file, "w") as f:
        json.dump(sample_colors, f)
    return colors_file


@pytest.fixture
def links_file(temp_dir, sample_links):
    """Create a temporary links.toml file."""
    import tomli_w

    links_file = temp_dir / "links.toml"
    with open(links_file, "wb") as f:
        tomli_w.dump(sample_links, f)
    return links_file


@pytest.fixture
def wallpaper_file(temp_dir):
    """Create a temporary wallpaper reference file."""
    wallpaper_file = temp_dir / ".wallpaper"
    wallpaper_path = temp_dir / "test_wallpaper.png"

    # Create a minimal PNG file
    wallpaper_path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    wallpaper_file.write_text(str(wallpaper_path))
    return wallpaper_file


# Flask app fixtures
@pytest.fixture
def app():
    """Create Flask test app."""
    from homepage.app import app as flask_app

    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


# Common mock builders for reuse
class MockResponseBuilder:
    """Builder for creating mock HTTP responses."""

    @staticmethod
    def create(content=None, status_code=200, headers=None, json_data=None):
        """Create a mock response with optional JSON."""
        mock = Mock()
        mock.status_code = status_code
        mock.headers = headers or {}
        mock.content = content or b""

        if json_data is not None:
            mock.json.return_value = json_data

        if status_code >= 400:

            def raise_for_status():
                import requests

                raise requests.HTTPError()

            mock.raise_for_status = raise_for_status

        return mock


class WeatherMockBuilder:
    """Builder for creating mock weather responses."""

    @staticmethod
    def openmeteo_current(temperature=15.0, humidity=70, code=0, wind=10.0):
        """Create mock Open-Meteo current weather response."""
        return {
            "current": {
                "temperature_2m": temperature,
                "relative_humidity_2m": humidity,
                "weather_code": code,
                "wind_speed_10m": wind,
            }
        }

    @staticmethod
    def openmeteo_hourly(num_hours=14):
        """Create mock Open-Meteo hourly forecast response."""
        from datetime import datetime

        now = datetime.now()
        current_hour = now.hour
        times = [f"2025-11-07T{h:02d}:00" for h in range(current_hour, current_hour + num_hours)]
        temps = [14.5 + i * 0.5 for i in range(len(times))]
        codes = list(range(num_hours))
        precips = list(range(num_hours))

        return {
            "hourly": {
                "time": times,
                "temperature_2m": temps,
                "weather_code": codes,
                "precipitation_probability": precips,
            }
        }

    @staticmethod
    def openmeteo_daily():
        """Create mock Open-Meteo daily forecast response."""
        return {
            "daily": {
                "time": [
                    "2025-11-07",
                    "2025-11-08",
                    "2025-11-09",
                    "2025-11-10",
                    "2025-11-11",
                    "2025-11-12",
                    "2025-11-13",
                ],
                "temperature_2m_max": [16.0, 15.5, 14.0, 13.5, 12.0, 11.5, 11.0],
                "temperature_2m_min": [10.0, 9.5, 8.0, 7.5, 6.0, 5.5, 5.0],
                "weather_code": [0, 1, 2, 3, 4, 5, 6],
                "precipitation_probability_max": [0, 10, 20, 30, 40, 50, 60],
            }
        }


@pytest.fixture
def mock_response_builder():
    """Provide MockResponseBuilder to tests."""
    return MockResponseBuilder


@pytest.fixture
def weather_mock_builder():
    """Provide WeatherMockBuilder to tests."""
    return WeatherMockBuilder
