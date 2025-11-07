# WebSocket Support

Real-time bidirectional communication for instant updates without polling.

## Overview

The Homepage application now supports WebSocket connections for real-time updates. Instead of polling the server every few seconds to check for changes, the server can push updates immediately to all connected clients.

## Features

- **Real-time Configuration Updates**: Instant page reload when colors, wallpaper, or links change
- **Live System Stats**: Push system statistics to clients in real-time (when enabled)
- **Weather Updates**: Push weather data updates via WebSocket
- **RSS Feed Updates**: Notify clients when RSS feeds are refreshed
- **Automatic Reconnection**: Exponential backoff strategy for reliable connections
- **Graceful Fallback**: Falls back to polling if WebSocket is unavailable
- **Multi-client Support**: Broadcasts updates to all connected clients simultaneously
- **Connection Health**: Automatic ping/pong for connection monitoring

## Architecture

### Backend (Flask-SocketIO)

The WebSocket implementation uses [Flask-SocketIO](https://flask-socketio.readthedocs.io/), which provides:

- **Socket.IO Protocol**: Reliable WebSocket communication with fallbacks
- **Multiple Transports**: WebSocket, polling (if WebSocket unavailable)
- **Event System**: Named events for different update types
- **Broadcasting**: Send messages to all connected clients
- **Async Modes**: Threading (default), eventlet, or gevent

### Frontend (Socket.IO Client)

The client-side implementation includes:

- **WebSocketClient Class**: Manages connection lifecycle
- **Auto-reconnection**: Exponential backoff with configurable limits
- **Event Handlers**: Subscribe to specific update events
- **Connection Status**: Monitor connection state
- **Fallback to Polling**: Automatic fallback if WebSocket fails

## Configuration

### Environment Variables

Enable WebSocket and configure its behavior:

```bash
# Enable/disable WebSocket (default: True)
HOMEPAGE_ENABLE_WEBSOCKET=True

# Async mode: threading, eventlet, or gevent (default: threading)
HOMEPAGE_WEBSOCKET_ASYNC_MODE=threading

# Ping timeout in seconds (default: 60)
HOMEPAGE_WEBSOCKET_PING_TIMEOUT=60

# Ping interval in seconds (default: 25)
HOMEPAGE_WEBSOCKET_PING_INTERVAL=25
```

### In `.env` File

```env
# WebSocket Configuration
HOMEPAGE_ENABLE_WEBSOCKET=True
HOMEPAGE_WEBSOCKET_ASYNC_MODE=threading
HOMEPAGE_WEBSOCKET_PING_TIMEOUT=60
HOMEPAGE_WEBSOCKET_PING_INTERVAL=25
```

### Programmatic Configuration

```python
from homepage.config import Config

class ProductionConfig(Config):
    ENABLE_WEBSOCKET = True
    WEBSOCKET_ASYNC_MODE = "threading"
    WEBSOCKET_PING_TIMEOUT = 60
    WEBSOCKET_PING_INTERVAL = 25
```

## WebSocket Events

### Server → Client Events

Events sent from server to connected clients:

#### `connected`

Sent when client successfully connects.

```javascript
{
  "status": "ok",
  "message": "Connected to homepage server"
}
```

#### `config_changed`

Configuration file has changed.

```javascript
{
  "type": "colors|wallpaper|links",
  "timestamp": 1234567890,
  "action": "reload"
}
```

#### `system_stats_update`

Real-time system statistics (if enabled).

```javascript
{
  "cpu_percent": 45.2,
  "memory_percent": 62.1,
  "disk_percent": 70.5,
  "network_sent_mb": 123.4,
  "network_recv_mb": 234.5,
  // ... additional stats
}
```

#### `weather_update`

Weather data has been updated.

```javascript
{
  "temperature": 20.5,
  "humidity": 65,
  "description": "Sunny",
  "location": "Amsterdam",
  "units": "metric"
}
```

#### `rss_update`

RSS feeds have been refreshed.

```javascript
{
  "items": [
    {
      "title": "Article Title",
      "link": "https://example.com/article",
      "published": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### `links_update`

Links configuration has been updated.

```javascript
{
  "categories": [
    {
      "name": "Development",
      "icon": "💻",
      "links": [...]
    }
  ]
}
```

#### `pong`

Response to client ping.

```javascript
{
  "timestamp": 1234567890
}
```

### Client → Server Events

Events sent from client to server:

#### `ping`

Health check to verify connection.

```javascript
// Client sends
{ "timestamp": 1234567890 }

// Server responds with 'pong' event
```

## API Endpoints

### `/api/websocket/status`

Get WebSocket connection status.

**Response:**

```json
{
  "enabled": true,
  "connected_clients": 3,
  "message": "WebSocket service is active"
}
```

### `/api/websocket/info`

Get detailed WebSocket configuration.

**Response:**

```json
{
  "enabled": true,
  "async_mode": "threading",
  "ping_timeout": 60,
  "ping_interval": 25,
  "connected_clients": 3
}
```

## Client-Side Usage

### Basic Setup

The WebSocket client is automatically initialized when the page loads:

```javascript
// Global instance available
window.wsClient

// Check if enabled
if (wsClient.isEnabled()) {
  console.log('WebSocket is active');
}

// Check connection status
if (wsClient.isConnected()) {
  console.log('Connected to server');
}
```

### Event Handling

Subscribe to WebSocket events:

```javascript
// Listen for configuration changes
wsClient.on('config_changed', (data) => {
  console.log('Config changed:', data.type);
  // Handle reload, update UI, etc.
});

// Listen for system stats
wsClient.on('system_stats_update', (data) => {
  console.log('CPU:', data.cpu_percent + '%');
  // Update stats display
});

// Listen for weather updates
wsClient.on('weather_update', (data) => {
  console.log('Weather:', data.temperature + '°C');
  // Update weather widget
});

// Listen for connection events
wsClient.on('ws_connected', () => {
  console.log('WebSocket connected!');
});

wsClient.on('ws_disconnected', (data) => {
  console.log('WebSocket disconnected:', data.reason);
});

wsClient.on('ws_failed', () => {
  console.log('WebSocket failed after max retries');
});
```

### Sending Events

Send custom events to server:

```javascript
// Send ping
wsClient.ping();

// Send custom event
wsClient.send('custom_event', {
  data: 'value'
});
```

### Connection Management

```javascript
// Manually disconnect
wsClient.disconnect();

// Manually reconnect
wsClient.connect();

// Get reconnection attempts
const attempts = wsClient.getReconnectAttempts();
console.log('Reconnect attempts:', attempts);
```

## Server-Side Usage

### Emitting Events

From route handlers or services:

```python
from homepage.services import get_websocket_service

# Get WebSocket service
ws = get_websocket_service()

# Emit configuration change
ws.emit_config_change('colors')

# Emit system stats
ws.emit_system_stats({
    'cpu_percent': 45.2,
    'memory_percent': 62.1
})

# Emit weather update
ws.emit_weather_update({
    'temperature': 20.5,
    'description': 'Sunny'
})

# Emit RSS update
ws.emit_rss_update({
    'items': [...]
})

# Emit links update
ws.emit_links_update(categories_data)
```

### File Watcher Integration

The file watcher automatically emits WebSocket events when configuration files change:

```python
# In ConfigFileHandler.on_modified()
match file_path.name:
    case "colors.json":
        if websocket_service and websocket_service.is_enabled():
            websocket_service.emit_config_change("colors")
    case ".wallpaper":
        if websocket_service and websocket_service.is_enabled():
            websocket_service.emit_config_change("wallpaper")
    case "links.toml" | "links.override.toml":
        if websocket_service and websocket_service.is_enabled():
            websocket_service.emit_config_change("links")
```

### Custom Events

Define custom event handlers:

```python
from homepage.services.websocket_service import WebSocketService

def init_custom_handlers(ws: WebSocketService):
    """Initialize custom WebSocket handlers."""
    if not ws.socketio:
        return
    
    @ws.socketio.on('custom_event')
    def handle_custom_event(data):
        """Handle custom event from client."""
        print(f'Received custom event: {data}')
        # Process data
        # Emit response
        emit('custom_response', {'status': 'ok'})
```

## Deployment Considerations

### Production Deployment

**Important**: The built-in Werkzeug server is suitable for development and simple deployments, but for production use, you should use a proper WSGI server.

#### Recommended: Gunicorn with Gevent

```bash
# Install gunicorn with gevent worker
pip install gunicorn gevent gevent-websocket

# Configure async mode
export HOMEPAGE_WEBSOCKET_ASYNC_MODE=gevent

# Run with gunicorn
gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:5000 "homepage.app:app"
```

#### Alternative: Eventlet

For production deployments, consider using eventlet or gevent for better scalability:

```bash
# Install eventlet
pip install eventlet

# Configure async mode
export HOMEPAGE_WEBSOCKET_ASYNC_MODE=eventlet

# Run with gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 "homepage.app:app"
```

**Note**: When using `allow_unsafe_werkzeug=True` (current default), you'll see a warning. This is acceptable for simple deployments, but production systems should use gunicorn or another production WSGI server.

### Reverse Proxy (Nginx)

WebSocket requires special proxy configuration:

```nginx
location /socket.io {
    proxy_pass http://localhost:5000/socket.io;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Timeouts
    proxy_connect_timeout 7d;
    proxy_send_timeout 7d;
    proxy_read_timeout 7d;
}
```

### Docker

WebSocket works seamlessly in Docker. Ensure port mapping is correct:

```yaml
# docker-compose.yml
services:
  homepage:
    ports:
      - "5000:5000"
    environment:
      - HOMEPAGE_ENABLE_WEBSOCKET=True
```

### Systemd Service

For simple deployments, the default systemd service configuration works fine. For production:

**Development/Simple Deployment** (current default):
```ini
[Service]
ExecStart=/path/to/venv/bin/python -m homepage.app
```

**Production Deployment** (recommended):
```ini
[Service]
ExecStart=/path/to/venv/bin/gunicorn --worker-class gevent -w 1 --bind 127.0.0.1:5000 "homepage.app:app"
Environment="HOMEPAGE_WEBSOCKET_ASYNC_MODE=gevent"
```

WebSocket runs on the same port as the Flask app in both cases.

## Monitoring

### Check Connection Status

```bash
# Via API
curl http://localhost:5000/api/websocket/status

# Response
{
  "enabled": true,
  "connected_clients": 3,
  "message": "WebSocket service is active"
}
```

### Check Configuration

```bash
curl http://localhost:5000/api/websocket/info
```

### Server Logs

WebSocket connections are logged:

```
INFO - Client connected (total: 3)
INFO - Configuration file changed: colors.json
INFO - Emitting config change: colors
INFO - Client disconnected (remaining: 2)
```

## Troubleshooting

### WebSocket Not Connecting

1. **Check if enabled:**
   ```bash
   curl http://localhost:5000/api/websocket/status
   ```

2. **Verify Socket.IO client library loaded:**
   - Check browser console for errors
   - Ensure CDN is accessible: `https://cdn.socket.io/4.7.2/socket.io.min.js`

3. **Check browser console:**
   ```javascript
   console.log('WebSocket enabled:', wsClient.isEnabled());
   console.log('WebSocket connected:', wsClient.isConnected());
   ```

### Connection Drops

WebSocket uses automatic reconnection with exponential backoff:

- **Initial delay:** 1 second
- **Max delay:** 30 seconds
- **Max attempts:** 10

After max attempts, falls back to polling.

### CORS Issues

Socket.IO is configured with `cors_allowed_origins="*"`. For production, restrict origins:

```python
self.socketio = SocketIO(
    app,
    cors_allowed_origins=["https://yourdomain.com"],
    # ... other settings
)
```

### Reverse Proxy Issues

Ensure proxy properly handles WebSocket upgrade:

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

## Performance

### Resource Usage

WebSocket connections are lightweight:

- **Memory:** ~50KB per connection
- **CPU:** Minimal (event-driven)
- **Network:** Only when events occur

### Scaling

For high-traffic deployments:

1. **Use eventlet/gevent** for async I/O
2. **Enable compression** (handled by Flask-SocketIO)
3. **Consider Redis** for multi-process deployments:

```python
from flask_socketio import SocketIO

socketio = SocketIO(
    app,
    message_queue='redis://localhost:6379/0',
    # ... other settings
)
```

## Migration from Polling

If upgrading from polling-based version:

1. **WebSocket is enabled by default** - no action needed
2. **Polling still available** as fallback
3. **Can disable WebSocket** if needed: `HOMEPAGE_ENABLE_WEBSOCKET=False`
4. **No breaking changes** - page reload mechanism works identically

## Security

### Authentication

WebSocket connections inherit Flask session authentication. For custom auth:

```python
from flask_socketio import disconnect

@socketio.on('connect')
def handle_connect():
    """Authenticate WebSocket connection."""
    if not user_is_authenticated():
        disconnect()
        return False
    # Connection allowed
```

### Rate Limiting

Prevent abuse with connection limits:

```python
from flask_limiter import Limiter

limiter = Limiter(app)

@socketio.on('connect')
@limiter.limit("10 per minute")
def handle_connect():
    pass
```

## Examples

### Complete Integration Example

```python
# app.py
from homepage.services import init_websocket_service

# Initialize
websocket_service = init_websocket_service(app, config)

# Emit from anywhere
def update_configuration():
    # Update config file
    save_config()
    
    # Notify all clients
    if websocket_service and websocket_service.is_enabled():
        websocket_service.emit_config_change('links')
```

### Frontend Integration Example

```javascript
// Custom event handler
wsClient.on('config_changed', (data) => {
    if (data.type === 'links' && !editMode) {
        // Reload only if not editing
        setTimeout(() => window.location.reload(), 500);
    }
});

// Connection status indicator
wsClient.on('ws_connected', () => {
    document.getElementById('status').textContent = '🟢 Live';
});

wsClient.on('ws_disconnected', () => {
    document.getElementById('status').textContent = '🟡 Reconnecting...';
});

wsClient.on('ws_failed', () => {
    document.getElementById('status').textContent = '🔴 Offline';
});
```

## Further Reading

- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [Socket.IO Protocol](https://socket.io/docs/v4/)
- [WebSocket RFC 6455](https://tools.ietf.org/html/rfc6455)
- [Deployment Best Practices](https://flask-socketio.readthedocs.io/en/latest/deployment.html)

## Support

For issues or questions:

1. Check server logs: `journalctl --user -u homepage.service -f`
2. Check browser console for client errors
3. Test WebSocket status: `curl http://localhost:5000/api/websocket/status`
4. Fall back to polling if needed: `HOMEPAGE_ENABLE_WEBSOCKET=False`
