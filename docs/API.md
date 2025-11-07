# Homepage API Documentation

This document describes the API endpoints available in the Homepage application.

## Base URL

When running locally: `http://localhost:5000`

## Endpoints

### GET /

**Description:** Main homepage endpoint that renders the application interface.

**Response:** HTML page with links, search, and clock

**Status Codes:**
- 200: Success

---

### GET /health

**Description:** Health check endpoint for monitoring application status.

**Response:**
```json
{
  "status": "healthy",
  "uptime": 123.45,
  "version": "2.0.0"
}
```

**Status Codes:**
- 200: Application is healthy

**Example:**
```bash
curl http://localhost:5000/health
```

---

### GET /api/stats

**Description:** Get application usage statistics and metrics.

**Response:**
```json
{
  "uptime_seconds": 3600.5,
  "uptime_formatted": "1h 0m 0s",
  "request_count": 150,
  "page_views": 50,
  "search_count": 25,
  "link_clicks_total": 75,
  "top_links": [
    ["GitHub", 20],
    ["Google Drive", 15]
  ],
  "search_providers": {
    "brave": 10,
    "google": 15
  },
  "recent_events_count": 100
}
```

**Status Codes:**
- 200: Success
- 404: Metrics not enabled

**Example:**
```bash
curl http://localhost:5000/api/stats
```

---

### POST /api/track

**Description:** Track user events (searches, link clicks).

**Request Body:**
```json
{
  "event": "search",
  "data": {
    "provider": "brave",
    "query": "test query"
  },
  "timestamp": 1234567890
}
```

Or for link clicks:
```json
{
  "event": "link_click",
  "data": {
    "name": "GitHub",
    "url": "https://github.com"
  },
  "timestamp": 1234567890
}
```

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- 200: Event tracked successfully
- 500: Error tracking event

**Example:**
```bash
curl -X POST http://localhost:5000/api/track \
  -H "Content-Type: application/json" \
  -d '{"event":"search","data":{"provider":"brave","query":"test"}}'
```

---

### GET /check_reload

**Description:** Check if a page reload is needed due to configuration changes.

**Response:**
```json
{
  "reload": false
}
```

**Status Codes:**
- 200: Success

**Notes:**
- Returns `true` when colors, wallpaper, or links configuration has changed
- Called automatically by the frontend every 2 seconds (configurable)
- Triggers automatic page reload when `reload` is `true`

---

### GET /api/favicon

**Description:** Fetch and cache favicon for a given URL with dark mode optimization.

**Query Parameters:**
- `url` (required): The URL to fetch the favicon for

**Response:**
```json
{
  "favicon": "data:image/png;base64,iVBORw0KG...",
  "cached": false
}
```

**Status Codes:**
- 200: Favicon fetched successfully
- 400: Missing or invalid URL parameter
- 404: Favicon not found
- 500: Server error

**Behavior:**
1. Checks cache for previously fetched favicon
2. Attempts direct extraction from webpage HTML with dark mode preference:
   - Explicit dark mode favicons (`media="(prefers-color-scheme: dark)"`)
   - SVG favicons (resolution-independent, often dark-friendly)
   - Standard favicon tags
3. Falls back to `/favicon.ico` at domain root
4. Falls back to Google's favicon service if direct extraction fails
5. Caches successful results for 1 hour

**Dark Mode Optimization:**
- Prioritizes SVG favicons which are resolution-independent
- Detects and uses explicit dark mode favicons when available
- Skips light-mode specific icons on dark backgrounds
- CSS filters applied for better visibility on dark backgrounds

**Example:**
```bash
curl "http://localhost:5000/api/favicon?url=https://github.com"
```

**Notes:**
- Favicons are converted to base64 data URIs for easy embedding
- SVG favicons provide better quality and dark mode compatibility
- Direct extraction provides better quality than external services
- Cache reduces network requests and improves performance
- Google fallback ensures reliability when direct extraction fails

---

### GET /wallpaper

**Description:** Serve the configured wallpaper image.

**Response:** Image file (JPEG, PNG, etc.) or 1x1 transparent PNG if no wallpaper configured

**Status Codes:**
- 200: Success

**Notes:**
- Wallpaper path is read from `~/.wallpaper` file
- Falls back to transparent PNG if file not found

---

### GET /favicon

**Description:** Serve the application favicon.

**Response:** SVG image with dynamic colors based on theme

**Status Codes:**
- 200: Success

**Content-Type:** `image/svg+xml`

---

## Configuration

### Environment Variables

Control API behavior using environment variables:

- `HOMEPAGE_HOST`: Host to bind to (default: `127.0.0.1`)
- `HOMEPAGE_PORT`: Port to listen on (default: `5000`)
- `HOMEPAGE_ENABLE_METRICS`: Enable metrics collection (default: `True`)
- `HOMEPAGE_ENABLE_CACHE`: Enable response caching (default: `True`)
- `HOMEPAGE_ENABLE_COMPRESSION`: Enable gzip compression (default: `True`)
- `HOMEPAGE_CACHE_TTL`: Cache time-to-live in seconds (default: `5`)
- `HOMEPAGE_RELOAD_INTERVAL`: Reload check interval in ms (default: `2000`)

### Example

```bash
export HOMEPAGE_PORT=8080
export HOMEPAGE_ENABLE_METRICS=True
python app.py
```

---

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting for production use with libraries like `Flask-Limiter`.

---

## CORS

CORS is not enabled by default. For cross-origin requests, configure Flask-CORS:

```python
from flask_cors import CORS
CORS(app)
```

---

## Error Handling

All endpoints return JSON error responses in this format:

```json
{
  "error": "Error message description"
}
```

Common error status codes:
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

---

## Metrics Export

Export metrics to a file using the CLI:

```bash
python cli.py stats --export metrics.json
```

Or use Make:

```bash
make export-metrics
```

---

## Monitoring

### Health Checks

Use the `/health` endpoint for monitoring:

```bash
# Simple check
curl -f http://localhost:5000/health || echo "Service down"

# In Docker
HEALTHCHECK CMD curl -f http://localhost:5000/health || exit 1
```

### Prometheus Integration

To integrate with Prometheus, consider adding `prometheus-flask-exporter`:

```python
from prometheus_flask_exporter import PrometheusMetrics
PrometheusMetrics(app)
```

---

## WebSocket Support

WebSocket support is not currently implemented. For real-time updates, the application uses polling via `/check_reload`.

---

## API Versioning

Current version: `v2.0.0`

The API is currently unversioned. Future versions may include `/api/v1/` prefix for backward compatibility.

---

## Examples

### Check if app is running
```bash
curl http://localhost:5000/health
```

### Get statistics
```bash
curl http://localhost:5000/api/stats | jq .
```

### Export metrics to file
```bash
curl http://localhost:5000/api/stats > stats.json
```

### Monitor uptime
```bash
watch -n 5 'curl -s http://localhost:5000/health | jq .uptime'
```
