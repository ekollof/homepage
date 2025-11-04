"""Pytest configuration and fixtures."""

import json
import tempfile
from pathlib import Path

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
