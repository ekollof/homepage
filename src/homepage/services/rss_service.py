"""RSS feed service."""

import logging
from typing import Any

import feedparser

logger = logging.getLogger(__name__)


class RSSService:
    """Service for fetching and parsing RSS feeds."""

    @staticmethod
    def fetch_feeds(
        feed_urls: list[str], max_items_per_feed: int = 5, cache_ttl: int = 300
    ) -> list[dict[str, Any]]:
        """Load and parse RSS feeds.

        Args:
            feed_urls: List of RSS feed URLs to fetch
            max_items_per_feed: Maximum items to fetch per feed
            cache_ttl: Cache TTL in seconds (unused, for future caching)

        Returns:
            List of feed items with title, link, description, published date.
        """
        all_items: list[dict[str, Any]] = []

        for feed_url in feed_urls:
            if not feed_url.strip():
                continue

            try:
                feed = feedparser.parse(feed_url)

                if not hasattr(feed, "entries") or not feed.entries:
                    continue

                for entry in feed.entries[:max_items_per_feed]:
                    # feedparser entries are dict-like
                    title = entry.get("title", "No title") if hasattr(entry, "get") else "No title"
                    link = entry.get("link", "") if hasattr(entry, "get") else ""
                    summary = (
                        entry.get("summary", entry.get("description", ""))
                        if hasattr(entry, "get")
                        else ""
                    )
                    description = summary[:200] if summary else ""
                    published = (
                        entry.get("published", entry.get("updated", ""))
                        if hasattr(entry, "get")
                        else ""
                    )
                    feed_title = "Unknown Feed"
                    if hasattr(feed, "feed") and hasattr(feed.feed, "get"):
                        feed_title = feed.feed.get(  # type: ignore[union-attr]
                            "title", "Unknown Feed"
                        )

                    item = {
                        "title": title,
                        "link": link,
                        "description": description,
                        "published": published,
                        "feed_title": feed_title,
                    }
                    all_items.append(item)

            except Exception as e:  # pylint: disable=broad-except
                logger.error("Error fetching RSS feed %s: %s", feed_url, e)
                continue

        return all_items
