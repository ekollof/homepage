"""Utility functions for the Homepage application."""

import json
import sys
import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class SimpleCache:
    """Simple in-memory cache with TTL support."""

    __slots__ = ("cache", "ttl")

    def __init__(self, ttl: int = 5):
        """Initialize cache with time-to-live in seconds."""
        self.cache: dict[str, tuple[Any, float]] = {}
        self.ttl = ttl

    def get(self, key: str) -> Any | None:
        """Get value from cache if not expired."""
        if (cached := self.cache.get(key)) is not None:
            value, timestamp = cached
            if time.time() - timestamp < self.ttl:
                return value
            del self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp."""
        self.cache[key] = (value, time.time())

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
