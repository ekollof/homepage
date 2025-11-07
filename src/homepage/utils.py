"""Utility functions for the Homepage application."""

import base64
import json
import logging
import sys
import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL support."""

    __slots__ = ("cache", "ttl")

    def __init__(self, ttl: int = 5):
        """Initialize cache with time-to-live in seconds."""
        self.cache: dict[str, tuple[Any, float, int]] = {}
        self.ttl = ttl

    def get(self, key: str) -> Any | None:
        """Get value from cache if not expired."""
        if (cached := self.cache.get(key)) is not None:
            value, timestamp, item_ttl = cached
            if time.time() - timestamp < item_ttl:
                return value
            del self.cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with current timestamp and optional custom TTL."""
        item_ttl = ttl if ttl is not None else self.ttl
        self.cache[key] = (value, time.time(), item_ttl)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

    def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry."""
        if key in self.cache:
            del self.cache[key]


def cache_with_ttl(cache_instance: SimpleCache, key: str) -> Callable:
    """Decorator to cache function results with TTL."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cached_value = cache_instance.get(key)
            if cached_value is not None:
                return cached_value

            result = func(*args, **kwargs)
            cache_instance.set(key, result)
            return result

        return wrapper

    return decorator


def load_json_file(file_path: Path, default: Any = None) -> Any:
    """Load JSON file with error handling."""
    if not file_path.exists():
        return default

    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Failed to load {file_path}: {e}")
        return default


def load_toml_file(file_path: Path, default: Any = None) -> Any:
    """Load TOML file with error handling."""
    if not file_path.exists():
        return default

    try:
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError) as e:
        print(f"Warning: Failed to load {file_path}: {e}")
        return default


def load_text_file(file_path: Path, default: str = "") -> str:
    """Load text file with error handling."""
    if not file_path.exists():
        return default

    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read().strip()
    except OSError as e:
        print(f"Warning: Failed to load {file_path}: {e}")
        return default


def validate_url(url: str) -> bool:
    """Validate URL format."""
    return url.startswith(("http://", "https://"))


def merge_links_configs(base_config: dict, override_config: dict) -> dict:
    """Return override configuration if it exists, otherwise return base.

    Simple override strategy:
    - If override has content, use it completely (ignore base)
    - If override is empty/missing, use base
    - This allows full control including deletions
    """
    if override_config and "category" in override_config:
        return override_config
    return base_config


def validate_links_config(config: dict) -> tuple[bool, list[str]]:
    """Validate links configuration structure."""
    errors = []

    if "category" not in config:
        errors.append("Missing 'category' key in configuration")
        return False, errors

    categories = config.get("category", [])
    if not isinstance(categories, list):
        errors.append("'category' must be a list")
        return False, errors

    for i, category in enumerate(categories):
        if not isinstance(category, dict):
            errors.append(f"Category {i} is not a dictionary")
            continue

        if "name" not in category:
            errors.append(f"Category {i} missing 'name'")

        if "links" in category:
            for j, link in enumerate(category.get("links", [])):
                if not isinstance(link, dict):
                    errors.append(f"Category {i}, link {j} is not a dictionary")
                    continue

                if "url" not in link:
                    errors.append(f"Category {i}, link {j} missing 'url'")
                elif not validate_url(link["url"]):
                    errors.append(f"Category {i}, link {j} has invalid URL: {link['url']}")

                if "name" not in link:
                    errors.append(f"Category {i}, link {j} missing 'name'")

        if "subcategory" in category:
            for j, subcat in enumerate(category.get("subcategory", [])):
                if not isinstance(subcat, dict):
                    errors.append(f"Category {i}, subcategory {j} is not a dictionary")
                    continue

                if "name" not in subcat:
                    errors.append(f"Category {i}, subcategory {j} missing 'name'")

                if "links" in subcat:
                    for k, link in enumerate(subcat.get("links", [])):
                        if not isinstance(link, dict):
                            errors.append(
                                f"Category {i}, subcategory {j}, link {k} is not a dictionary"
                            )
                            continue

                        if "url" not in link:
                            errors.append(f"Category {i}, subcategory {j}, link {k} missing 'url'")
                        elif not validate_url(link["url"]):
                            url = link["url"]
                            errors.append(
                                f"Category {i}, subcategory {j}, link {k} "
                                f"has invalid URL: {url}"
                            )

                        if "name" not in link:
                            errors.append(f"Category {i}, subcategory {j}, link {k} missing 'name'")

    return len(errors) == 0, errors


def extract_favicon_from_page(url: str, timeout: int = 5) -> str | None:
    """Extract favicon from a webpage.

    Attempts to find favicon with preference for dark mode and adaptive versions.
    Search order:
    1. <link rel="icon" media="(prefers-color-scheme: dark)"> - Explicit dark mode favicon
    2. <link rel="icon" type="image/svg+xml"> - SVG favicons (often adaptive/dark-friendly)
    3. <link rel="icon"> - Standard favicon
    4. <link rel="shortcut icon"> - Legacy favicon
    5. <link rel="apple-touch-icon"> - Apple touch icon
    6. /favicon.ico - Standard location at domain root

    Returns base64 data URI if found, None otherwise.
    """
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.warning("Invalid URL for favicon extraction: %s", url)
            return None

        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Fetch the HTML page
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, "lxml")

        # Try to find favicon link tags with dark mode preference
        favicon_url = None
        favicon_type = None

        # Strategy 1: Look for explicit dark mode favicon
        dark_mode_link = soup.find(
            "link",
            rel=lambda r: r and "icon" in str(r).lower(),  # type: ignore[arg-type]
            attrs={"media": lambda m: m and "dark" in str(m).lower()},  # type: ignore[arg-type]
        )
        if dark_mode_link and dark_mode_link.get("href"):
            favicon_url = dark_mode_link["href"]
            favicon_type = "dark-mode-explicit"
            logger.debug("Found explicit dark mode favicon for %s", url)

        # Strategy 2: Prefer SVG icons (they're resolution-independent and often dark-friendly)
        if not favicon_url:
            svg_icon = soup.find(
                "link", rel=lambda r: r and "icon" in str(r).lower(), type="image/svg+xml"  # type: ignore[arg-type]
            )
            # Also check href for .svg extension
            if not svg_icon:
                svg_icon = soup.find(
                    "link",
                    rel=lambda r: r and "icon" in str(r).lower(),  # type: ignore[arg-type]
                    href=lambda h: h and ".svg" in str(h).lower(),  # type: ignore[arg-type]
                )

            if svg_icon and svg_icon.get("href"):
                # Skip mask-icon (used for Safari pinned tabs, not suitable for general use)
                if "mask-icon" not in str(svg_icon.get("rel", [])).lower():  # type: ignore[arg-type]
                    favicon_url = svg_icon["href"]
                    favicon_type = "svg"
                    logger.debug("Found SVG favicon for %s", url)

        # Strategy 3: Standard icon search (skip light-mode specific ones)
        if not favicon_url:
            for rel in ["icon", "shortcut icon", "apple-touch-icon"]:
                link_tag = soup.find("link", rel=rel)
                if link_tag and link_tag.get("href"):
                    # Check if this is explicitly a light mode icon (skip it)
                    media_attr = link_tag.get("media", "")
                    if media_attr and "light" in str(media_attr).lower():
                        continue
                    favicon_url = link_tag["href"]
                    favicon_type = "standard"
                    break

        # If found in HTML, make it absolute
        if favicon_url:
            favicon_url = urljoin(base_url, favicon_url)  # type: ignore[arg-type]
        else:
            # Fallback to /favicon.ico
            favicon_url = f"{base_url}/favicon.ico"
            favicon_type = "fallback"

        # Fetch the favicon
        favicon_response = requests.get(favicon_url, headers=headers, timeout=timeout)

        if favicon_response.status_code == 200 and len(favicon_response.content) > 0:
            # Convert to base64 data URI
            content_type = favicon_response.headers.get("Content-Type", "image/x-icon")

            # Override content type for SVG
            if favicon_type == "svg" or ".svg" in favicon_url.lower():
                content_type = "image/svg+xml"
            elif "image" not in content_type:
                # Normalize content type for non-image types
                content_type = "image/x-icon"

            favicon_base64 = base64.b64encode(favicon_response.content).decode("utf-8")
            return f"data:{content_type};base64,{favicon_base64}"

        return None

    except requests.Timeout:
        logger.warning("Timeout while fetching favicon for %s", url)
        return None
    except requests.RequestException as e:
        logger.debug("Failed to fetch favicon from page %s: %s", url, e)
        return None
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Unexpected error extracting favicon from %s: %s", url, e)
        return None


def fetch_favicon_google(domain: str, size: int = 64, timeout: int = 5) -> str | None:
    """Fetch favicon from Google's favicon service.

    Returns base64 data URI if successful, None otherwise.
    """
    try:
        favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz={size}"
        response = requests.get(favicon_url, timeout=timeout)

        if response.status_code == 200 and len(response.content) > 0:
            content_type = response.headers.get("Content-Type", "image/png")
            favicon_base64 = base64.b64encode(response.content).decode("utf-8")
            return f"data:{content_type};base64,{favicon_base64}"

        return None

    except requests.RequestException as e:
        logger.debug("Failed to fetch favicon from Google for %s: %s", domain, e)
        return None
