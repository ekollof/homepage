"""RSS feed API routes."""

import logging

from flask import Blueprint, jsonify

from ..services.rss_service import RSSService

logger = logging.getLogger(__name__)

rss_bp = Blueprint("rss", __name__)

_config = None
_cache = None


def init_rss_blueprint(config, cache):
    """Initialize RSS blueprint with dependencies."""
    global _config, _cache
    _config = config
    _cache = cache


@rss_bp.route("/api/rss")
def get_rss():
    """Get RSS feed items."""
    if not _config.ENABLE_RSS:
        return jsonify({"error": "RSS feature not enabled"}), 404

    try:
        # Check cache first
        cache_key = "rss_feeds"
        if _cache and (cached := _cache.get(cache_key)):
            return jsonify({"items": cached, "count": len(cached)})

        # Fetch feeds
        feeds = RSSService.fetch_feeds(
            feed_urls=_config.RSS_FEEDS,
            max_items_per_feed=_config.RSS_MAX_ITEMS,
            cache_ttl=_config.RSS_CACHE_TTL,
        )

        # Cache for RSS_CACHE_TTL seconds
        if _cache:
            _cache.set(cache_key, feeds, ttl=_config.RSS_CACHE_TTL)

        return jsonify({"items": feeds, "count": len(feeds)})
    except Exception as e:  # pylint: disable=broad-except
        logger.error("RSS error: %s", e)
        return jsonify({"error": "Failed to fetch RSS feeds"}), 500
