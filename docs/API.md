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

### GET /api/rss

**Description:** Get RSS feed items from configured feeds.

**Response:**
```json
{
  "items": [
    {
      "title": "Article Title",
      "link": "https://example.com/article",
      "description": "Article summary...",
      "published": "Mon, 10 Nov 2025 16:05:46 +0000",
      "feed_title": "Feed Name"
    }
  ],
  "count": 10
}
```

**Status Codes:**
- 200: Success
- 404: RSS feature not enabled
- 500: Error fetching feeds

**Configuration:**
- `HOMEPAGE_ENABLE_RSS=True` - Enable RSS feature
- `HOMEPAGE_RSS_FEEDS` - Pipe-separated feed URLs
- `HOMEPAGE_RSS_MAX_ITEMS` - Max items per feed (default: 5)
- `HOMEPAGE_RSS_CACHE_TTL` - Cache duration in seconds (default: 300)

**Example:**
```bash
curl http://localhost:5000/api/rss
```

---

### GET /api/weather

**Description:** Get current weather data for configured location.

**Response:**
```json
{
  "temperature": 15.5,
  "feels_like": 13.2,
  "description": "Partly cloudy",
  "icon": "⛅",
  "humidity": 65,
  "wind_speed": 12.5,
  "location": "Amsterdam, NL"
}
```

**Status Codes:**
- 200: Success
- 404: Weather feature not enabled
- 500: Error fetching weather data

**Configuration:**
- `HOMEPAGE_ENABLE_WEATHER=True` - Enable weather feature
- `HOMEPAGE_WEATHER_PROVIDER` - `openmeteo` or `openweathermap`
- `HOMEPAGE_WEATHER_LOCATION` - Optional `lat,lon` (auto-detects if empty)
- `HOMEPAGE_WEATHER_UNITS` - `metric` or `imperial`

**Example:**
```bash
curl http://localhost:5000/api/weather
```

---

### GET /api/weather/forecast

**Description:** Get hourly weather forecast.

**Response:**
```json
{
  "forecast": [
    {
      "time": "14:00",
      "temperature": 16,
      "icon": "☀️",
      "description": "Clear"
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 404: Weather feature not enabled

---

### GET /api/weather/forecast/daily

**Description:** Get daily weather forecast.

**Response:**
```json
{
  "forecast": [
    {
      "day": "Monday",
      "temp_high": 18,
      "temp_low": 12,
      "icon": "⛅",
      "description": "Partly cloudy"
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 404: Weather feature not enabled

---

### GET /api/system-stats

**Description:** Get real-time system statistics.

**Response:**
```json
{
  "cpu_percent": 25.5,
  "cpu_count": 8,
  "cpu_freq_current": 2400,
  "memory_percent": 45.2,
  "memory_used_gb": 7.2,
  "memory_total_gb": 16.0,
  "disk_percent": 60.5,
  "disk_used_gb": 120.5,
  "disk_total_gb": 200.0,
  "network_sent_mb": 1024.5,
  "network_recv_mb": 2048.3,
  "uptime_seconds": 86400
}
```

**Status Codes:**
- 200: Success
- 404: System stats feature not enabled
- 500: Error collecting stats

**Configuration:**
- `HOMEPAGE_ENABLE_SYSTEM_STATS=True` - Enable system stats
- `HOMEPAGE_SYSTEM_STATS_REFRESH_INTERVAL` - Update interval in seconds (default: 5)

**Example:**
```bash
curl http://localhost:5000/api/system-stats
```

---

### GET /api/config

**Description:** Get current links configuration (requires editing enabled).

**Response:**
```json
{
  "categories": [
    {
      "name": "Development",
      "icon": "💻",
      "links": [...],
      "subcategory": [...]
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 404: Editing feature not enabled

**Example:**
```bash
curl http://localhost:5000/api/config
```

---

### POST /api/config

**Description:** Save links configuration (requires editing enabled).

**Request Body:**
```json
{
  "categories": [...]
}
```

**Response:**
```json
{
  "status": "success"
}
```

**Status Codes:**
- 200: Configuration saved
- 400: Invalid configuration
- 404: Editing feature not enabled
- 500: Error saving configuration

**Example:**
```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"categories":[...]}'
```

---

### POST /api/config/reset

**Description:** Reset configuration to base (delete override file).

**Response:**
```json
{
  "status": "success",
  "message": "Configuration reset to base"
}
```

**Status Codes:**
- 200: Configuration reset
- 404: Editing feature not enabled

---

### GET /api/websocket/status

**Description:** Get WebSocket connection status and statistics.

**Response:**
```json
{
  "enabled": true,
  "connected_clients": 3,
  "async_mode": "threading"
}
```

**Status Codes:**
- 200: Success
- 404: WebSocket not enabled

---

### GET /api/websocket/info

**Description:** Get detailed WebSocket configuration.

**Response:**
```json
{
  "enabled": true,
  "async_mode": "threading",
  "ping_timeout": 60,
  "ping_interval": 25,
  "url": "ws://localhost:5000/socket.io/"
}
```

**Status Codes:**
- 200: Success

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

## WebSocket Events

WebSocket support is available when `HOMEPAGE_ENABLE_WEBSOCKET=True`.

### Connection

**Endpoint:** `ws://localhost:5000/socket.io/`

**Events from Server:**

#### `ws_connected`
Emitted when client successfully connects.

#### `config_changed`
Emitted when configuration files change.
```json
{
  "type": "colors|wallpaper|links",
  "message": "Configuration changed"
}
```

#### `system_stats_update`
Real-time system statistics (if enabled).
```json
{
  "cpu_percent": 25.5,
  "memory_percent": 45.2,
  ...
}
```

#### `weather_update`
Weather data updates (if enabled).
```json
{
  "temperature": 15.5,
  "description": "Partly cloudy",
  ...
}
```

#### `rss_update`
RSS feed updates (if enabled).
```json
{
  "items": [...],
  "count": 10
}
```

**Client Events:**

#### `connect`
Client initiates connection.

#### `disconnect`
Client disconnects.

**Configuration:**
- `HOMEPAGE_ENABLE_WEBSOCKET` - Enable WebSocket (default: True)
- `HOMEPAGE_WEBSOCKET_ASYNC_MODE` - `threading`, `eventlet`, or `gevent`
- `HOMEPAGE_WEBSOCKET_PING_TIMEOUT` - Ping timeout in seconds (default: 60)
- `HOMEPAGE_WEBSOCKET_PING_INTERVAL` - Ping interval in seconds (default: 25)

**Example (JavaScript):**
```javascript
const socket = io();

socket.on('connect', () => {
  console.log('Connected');
});

socket.on('config_changed', (data) => {
  console.log('Config changed:', data.type);
  location.reload();
});

socket.on('system_stats_update', (data) => {
  updateStatsDisplay(data);
});
```

---

## Configuration

### Environment Variables

Control API behavior using environment variables (set in `.env` file or systemd service):

**Core Settings:**
- `HOMEPAGE_HOST`: Host to bind to (default: `127.0.0.1`)
- `HOMEPAGE_PORT`: Port to listen on (default: `5000`)
- `HOMEPAGE_ENV`: `development` or `production`
- `HOMEPAGE_SECRET_KEY`: Flask secret key (auto-generated in production)
- `HOMEPAGE_DEBUG`: Enable debug mode (default: `False`)

**Feature Flags:**
- `HOMEPAGE_ENABLE_METRICS`: Enable metrics collection (default: `True`)
- `HOMEPAGE_ENABLE_WEATHER`: Enable weather widget (default: `False`)
- `HOMEPAGE_ENABLE_RSS`: Enable RSS feeds (default: `False`)
- `HOMEPAGE_ENABLE_SYSTEM_STATS`: Enable system stats (default: `True`)
- `HOMEPAGE_ENABLE_EDITING`: Enable in-browser editing (default: `True`)
- `HOMEPAGE_ENABLE_WEBSOCKET`: Enable WebSocket (default: `True`)

**Performance:**
- `HOMEPAGE_ENABLE_CACHE`: Enable response caching (default: `True`)
- `HOMEPAGE_ENABLE_COMPRESSION`: Enable gzip compression (default: `True`)
- `HOMEPAGE_CACHE_TTL`: Cache time-to-live in seconds (default: `5`)

**Weather Settings:**
- `HOMEPAGE_WEATHER_PROVIDER`: `openmeteo` or `openweathermap`
- `HOMEPAGE_WEATHER_API_KEY`: API key for OpenWeatherMap (if used)
- `HOMEPAGE_WEATHER_LOCATION`: Optional `lat,lon` (auto-detects if empty)
- `HOMEPAGE_WEATHER_UNITS`: `metric` or `imperial`
- `HOMEPAGE_GEOIP_PROVIDER`: `maxmind`, `ipapi`, or `ip-api`

**RSS Settings:**
- `HOMEPAGE_RSS_FEEDS`: Pipe-separated feed URLs
- `HOMEPAGE_RSS_MAX_ITEMS`: Max items per feed (default: `5`)
- `HOMEPAGE_RSS_CACHE_TTL`: Cache duration in seconds (default: `300`)

**System Stats:**
- `HOMEPAGE_SYSTEM_STATS_REFRESH_INTERVAL`: Update interval in seconds (default: `5`)
- `HOMEPAGE_SYSTEM_STATS_POSITION`: `left`, `right`, `top`, or `bottom`

**WebSocket:**
- `HOMEPAGE_WEBSOCKET_ASYNC_MODE`: `threading`, `eventlet`, or `gevent`
- `HOMEPAGE_WEBSOCKET_PING_TIMEOUT`: Ping timeout in seconds (default: `60`)
- `HOMEPAGE_WEBSOCKET_PING_INTERVAL`: Ping interval in seconds (default: `25`)

**UI Settings:**
- `HOMEPAGE_CLOCK_FORMAT`: `24` or `12`
- `HOMEPAGE_RELOAD_INTERVAL`: Reload check interval in ms (default: `2000`)
- `HOMEPAGE_WATCH_FILES`: Enable file watching (default: `True`)

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

**Status:** ✅ Implemented

WebSocket support is enabled by default for real-time updates. See the WebSocket Events section above for details.

**Features:**
- Real-time configuration change notifications
- Live system stats updates (if enabled)
- Weather and RSS updates via push
- Automatic reconnection with exponential backoff
- Graceful fallback to polling if WebSocket unavailable

**Documentation:** See `docs/WEBSOCKET.md` for detailed WebSocket documentation.

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
