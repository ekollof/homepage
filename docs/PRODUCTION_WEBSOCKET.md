# Production WebSocket Deployment Guide

This guide helps you upgrade from the default Werkzeug development server to a production-ready WebSocket deployment.

## Why Upgrade?

The default deployment uses Flask's built-in Werkzeug server with `allow_unsafe_werkzeug=True`. While this works fine for:
- Personal use
- Single-user deployments
- Testing and development
- Low-traffic scenarios

For production environments with multiple users or high traffic, you should use a proper WSGI server.

## Quick Upgrade (Recommended)

### Step 1: Install Gunicorn with Gevent

```bash
cd ~/devel/homepage
./venv/bin/pip install gunicorn gevent gevent-websocket
```

### Step 2: Update Environment Configuration

Edit or create `data/.env`:

```bash
# Use gevent for better WebSocket performance
HOMEPAGE_WEBSOCKET_ASYNC_MODE=gevent

# Set to production mode
HOMEPAGE_ENV=production
```

### Step 3: Update Systemd Service

Edit `~/.config/systemd/user/homepage.service`:

**Before:**
```ini
[Service]
WorkingDirectory=/home/YOUR_USERNAME/devel/homepage
ExecStart=/home/YOUR_USERNAME/devel/homepage/venv/bin/python -m homepage.app
```

**After:**
```ini
[Service]
WorkingDirectory=/home/YOUR_USERNAME/devel/homepage
ExecStart=/home/YOUR_USERNAME/devel/homepage/venv/bin/gunicorn \
    --worker-class gevent \
    -w 1 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --log-level info \
    "homepage.app:app"
EnvironmentFile=/home/YOUR_USERNAME/devel/homepage/data/.env
```

### Step 4: Reload and Restart

```bash
systemctl --user daemon-reload
systemctl --user restart homepage.service
systemctl --user status homepage.service
```

### Step 5: Verify

```bash
# Check WebSocket is still working
curl http://localhost:5000/api/websocket/status

# Should return:
# {"enabled": true, "connected_clients": 0, ...}
```

✅ **Done!** Your WebSocket deployment is now production-ready.

---

## Alternative: Eventlet

If you prefer eventlet over gevent:

### Install Eventlet

```bash
./venv/bin/pip install gunicorn eventlet
```

### Update Configuration

In `data/.env`:
```bash
HOMEPAGE_WEBSOCKET_ASYNC_MODE=eventlet
HOMEPAGE_ENV=production
```

### Update Systemd Service

```ini
ExecStart=/home/YOUR_USERNAME/devel/homepage/venv/bin/gunicorn \
    --worker-class eventlet \
    -w 1 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    "homepage.app:app"
```

---

## Configuration Options Explained

### Worker Class

- **`gevent`**: Green threads, excellent WebSocket support, recommended
- **`eventlet`**: Alternative green threads implementation
- **`threading`**: Default, works but not recommended for production

### Worker Count (`-w 1`)

**Important**: WebSocket applications should use **1 worker only** (or use Redis for multi-worker setups).

Why? WebSocket connections are stateful. Multiple workers without coordination can't share connection state.

For multi-worker deployments, see "Scaling" section below.

### Bind Address

- **`127.0.0.1:5000`**: Localhost only (recommended with reverse proxy)
- **`0.0.0.0:5000`**: All interfaces (use with caution, ensure firewall)

### Timeout

- **`120`**: Seconds before request timeout (generous for long-lived WebSocket connections)

---

## Reverse Proxy Setup (Nginx)

If you're running behind Nginx, update your configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Special WebSocket configuration
    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        
        # WebSocket upgrade headers
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Long-lived connection timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }
}
```

Reload Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## Scaling Beyond One Worker

For high-traffic deployments requiring multiple workers:

### 1. Install Redis

```bash
sudo apt install redis-server  # Ubuntu/Debian
# or
sudo dnf install redis  # Fedora
```

### 2. Install Redis Support

```bash
./venv/bin/pip install redis
```

### 3. Update Application

The WebSocket service would need to be configured with Redis message queue. Contact support or check Flask-SocketIO documentation for multi-worker setup.

**Note**: This is advanced and rarely needed for personal homepages.

---

## Docker Deployment

If using Docker, update your `docker-compose.yml`:

```yaml
version: '3.8'

services:
  homepage:
    build: .
    ports:
      - "5000:5000"
    environment:
      - HOMEPAGE_ENV=production
      - HOMEPAGE_WEBSOCKET_ASYNC_MODE=gevent
    command: >
      gunicorn
      --worker-class gevent
      -w 1
      --bind 0.0.0.0:5000
      --timeout 120
      "homepage.app:app"
```

Update `Dockerfile` to install gunicorn:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir gunicorn gevent gevent-websocket

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--worker-class", "gevent", "-w", "1", \
     "--bind", "0.0.0.0:5000", "--timeout", "120", "homepage.app:app"]
```

---

## Monitoring Production Deployment

### Check Service Status

```bash
systemctl --user status homepage.service
```

### View Logs

```bash
journalctl --user -u homepage.service -f
```

### Check WebSocket Connections

```bash
curl http://localhost:5000/api/websocket/info
```

### Monitor Resource Usage

```bash
# CPU and memory usage
ps aux | grep gunicorn

# Active connections
ss -tnp | grep :5000
```

---

## Performance Tuning

### Increase Worker Timeout (if needed)

For very slow connections:
```bash
gunicorn --timeout 300 ...  # 5 minutes
```

### Adjust Buffer Sizes

For high message throughput:
```bash
gunicorn --worker-connections 1000 ...
```

### Enable Logging

For debugging:
```bash
gunicorn --log-level debug --access-logfile - --error-logfile - ...
```

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
journalctl --user -u homepage.service -n 50
```

**Common issues:**
- Missing dependencies: Install gunicorn and gevent
- Wrong path in ExecStart: Verify paths in service file
- Port already in use: Check with `ss -tnlp | grep 5000`

### WebSocket Not Connecting

**Verify WebSocket endpoint:**
```bash
curl http://localhost:5000/api/websocket/status
```

**Check browser console:**
- Look for WebSocket connection errors
- Verify Socket.IO client loaded from CDN

**Test without reverse proxy:**
- Temporarily bypass Nginx to isolate issue

### Performance Issues

**Check worker class:**
```bash
ps aux | grep gunicorn
# Should show: --worker-class gevent
```

**Monitor connections:**
```bash
curl http://localhost:5000/api/websocket/info
# Check connected_clients count
```

**Check system resources:**
```bash
htop
# Look for high CPU/memory usage
```

---

## Rollback to Development Server

If you need to rollback:

### 1. Restore Systemd Service

```ini
[Service]
ExecStart=/home/YOUR_USERNAME/devel/homepage/venv/bin/python -m homepage.app
```

### 2. Reload and Restart

```bash
systemctl --user daemon-reload
systemctl --user restart homepage.service
```

### 3. Update Environment

In `data/.env`:
```bash
HOMEPAGE_WEBSOCKET_ASYNC_MODE=threading
HOMEPAGE_ENV=development
```

---

## Summary

**Recommended Production Setup:**
- ✅ Gunicorn with gevent worker class
- ✅ Single worker (`-w 1`)
- ✅ 120-second timeout
- ✅ Environment set to production
- ✅ Reverse proxy (Nginx) with WebSocket support
- ✅ Systemd service management

**Performance Benefits:**
- Better connection handling
- Lower resource usage
- Improved stability
- Proper production logging

**When to Upgrade:**
- Multiple users accessing simultaneously
- High traffic volume
- Public-facing deployment
- Professional/business use

**When Default is Fine:**
- Personal use only
- Single user
- Low traffic
- Local network only

---

## Support

For issues or questions:
1. Check service logs: `journalctl --user -u homepage.service -f`
2. Verify WebSocket status: `curl http://localhost:5000/api/websocket/status`
3. Review documentation: `docs/WEBSOCKET.md`
4. Test without gunicorn to isolate issue

## Further Reading

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Flask-SocketIO Deployment](https://flask-socketio.readthedocs.io/en/latest/deployment.html)
- [Gevent Documentation](http://www.gevent.org/)
- [Eventlet Documentation](https://eventlet.net/)