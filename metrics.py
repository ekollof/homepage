"""Metrics collection and tracking for Homepage application."""

import json
import time
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any


class MetricsCollector:
    """Collect and store application metrics."""

    __slots__ = (
        "max_events",
        "start_time",
        "request_count",
        "page_views",
        "search_count",
        "link_clicks",
        "search_providers",
        "recent_events",
        "lock",
    )

    def __init__(self, max_events: int = 1000):
        """Initialize metrics collector."""
        self.max_events = max_events
        self.start_time = time.time()
        self.request_count = 0
        self.page_views = 0
        self.search_count = 0
        self.link_clicks: defaultdict[str, int] = defaultdict(int)
        self.search_providers: defaultdict[str, int] = defaultdict(int)
        self.recent_events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self.lock = Lock()

    def track_request(self, endpoint: str) -> None:
        """Track a request to an endpoint."""
        with self.lock:
            self.request_count += 1
            if endpoint == "/":
                self.page_views += 1

    def track_search(self, provider: str, query: str) -> None:
        """Track a search event."""
        with self.lock:
            self.search_count += 1
            self.search_providers[provider] += 1
            self.recent_events.append(
                {
                    "type": "search",
                    "provider": provider,
                    "query": query,
                    "timestamp": time.time(),
                }
            )

    def track_link_click(self, link_name: str, url: str) -> None:
        """Track a link click."""
        with self.lock:
            self.link_clicks[link_name] += 1
            self.recent_events.append(
                {
                    "type": "link_click",
                    "name": link_name,
                    "url": url,
                    "timestamp": time.time(),
                }
            )

    def get_uptime(self) -> float:
        """Get application uptime in seconds."""
        return time.time() - self.start_time

    def get_stats(self) -> dict[str, Any]:
        """Get current statistics."""
        with self.lock:
            uptime = self.get_uptime()
            return {
                "uptime_seconds": uptime,
                "uptime_formatted": self._format_uptime(uptime),
                "request_count": self.request_count,
                "page_views": self.page_views,
                "search_count": self.search_count,
                "link_clicks_total": sum(self.link_clicks.values()),
                "top_links": self._get_top_items(self.link_clicks, 10),
                "search_providers": dict(self.search_providers),
                "recent_events_count": len(self.recent_events),
            }

    def get_recent_events(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent events."""
        with self.lock:
            events = list(self.recent_events)
            return events[-limit:]

    def export_to_file(self, file_path: Path) -> None:
        """Export metrics to JSON file."""
        stats = self.get_stats()
        stats["recent_events"] = self.get_recent_events()
        stats["all_link_clicks"] = dict(self.link_clicks)
        stats["export_time"] = datetime.now().isoformat()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Format uptime in human-readable format."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if days > 0:
            return f"{days}d {hours}h {minutes}m {secs}s"
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        if minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"

    @staticmethod
    def _get_top_items(items_dict: dict, limit: int) -> list[tuple[str, int]]:
        """Get top N items from a dictionary."""
        return sorted(items_dict.items(), key=lambda x: x[1], reverse=True)[:limit]
