# Deployment Guide

This guide covers different deployment options for the Homepage application.

## Table of Contents

- [Local Development](#local-development)
- [Systemd Service](#systemd-service)
- [Docker](#docker)
- [Docker Compose](#docker-compose)
- [Reverse Proxy Setup](#reverse-proxy-setup)
- [Production Considerations](#production-considerations)

---

## Local Development

For development and testing:

```bash
# Install dependencies
make install-dev

# Run application
make run

# Or with custom settings
export HOMEPAGE_PORT=8080
export HOMEPAGE_DEBUG=True
python app.py
```

Access at http://localhost:5000

---

## Systemd Service

For running as a background service on Linux:

### Quick Setup

The installation script automatically configures the correct paths:

```bash
# Install and start service (recommended)
./install.sh

# Or manually
make service-install
make service-enable
make service-start
```

The installer will automatically:
- Detect the installation directory
- Configure the service with correct paths
- Install to `~/.config/systemd/user/homepage.service`

### Manual Configuration

If you need to manually create the service file:

1. Replace `/path/to/homepage` with your actual installation path:

```bash
INSTALL_DIR="/path/to/homepage"
sed "s|INSTALL_DIR_PLACEHOLDER|$INSTALL_DIR|g" homepage.service > ~/.config/systemd/user/homepage.service
```

2. Or create `~/.config/systemd/user/homepage.service` directly:

```ini
[Unit]
Description=Homepage Web Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/homepage
ExecStart=/path/to/homepage/venv/bin/python app.py
Restart=on-failure
RestartSec=10
Environment="PATH=/path/to/homepage/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="HOMEPAGE_ENV=production"
Environment="HOMEPAGE_HOST=127.0.0.1"
Environment="HOMEPAGE_PORT=5000"

[Install]
WantedBy=default.target
```

2. Reload and start:

```bash
systemctl --user daemon-reload
systemctl --user enable homepage.service
systemctl --user start homepage.service
```

**Note**: Replace `/path/to/homepage` with your actual installation directory in the service file.

### Service Management

```bash
# Check status
systemctl --user status homepage.service

# View logs
journalctl --user -u homepage.service -f

# Restart after config changes
systemctl --user restart homepage.service

# Stop service
systemctl --user stop homepage.service

# Disable auto-start
systemctl --user disable homepage.service
```

---

## Docker

### Build Image

```bash
# Build the image
docker build -t homepage:latest .

# Or use make
make docker-build
```

### Run Container

```bash
docker run -d \
  --name homepage \
  -p 5000:5000 \
  -v $(pwd)/links.toml:/app/links.toml:ro \
  -v ~/.cache/wal:/root/.cache/wal:ro \
  -v ~/.wallpaper:/root/.wallpaper:ro \
  -e HOMEPAGE_ENV=production \
  homepage:latest
```

### Container Management

```bash
# View logs
docker logs -f homepage

# Stop container
docker stop homepage

# Remove container
docker rm homepage

# Execute commands in container
docker exec -it homepage python cli.py health
```

---

## Docker Compose

### Setup

1. Copy environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings

3. Start services:
```bash
docker-compose up -d

# Or use make
make docker-run
```

### Configuration

Edit `docker-compose.yml` to customize:

```yaml
services:
  homepage:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./links.toml:/app/links.toml:ro
      - ~/.cache/wal:/root/.cache/wal:ro
    environment:
      - HOMEPAGE_ENV=production
      - HOMEPAGE_PORT=5000
    restart: unless-stopped
```

### Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and restart
docker-compose up -d --build

# Check status
docker-compose ps
```

---

## Reverse Proxy Setup

### Nginx

For external access through Nginx:

```nginx
server {
    listen 80;
    server_name homepage.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Optional: Add security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
}
```

With SSL (Let's Encrypt):

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d homepage.example.com

# Auto-renewal is configured automatically
```

### Apache

For Apache reverse proxy:

```apache
<VirtualHost *:80>
    ServerName homepage.example.com
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
</VirtualHost>
```

Enable required modules:

```bash
sudo a2enmod proxy proxy_http headers
sudo systemctl restart apache2
```

### Caddy

Caddy with automatic HTTPS:

```
homepage.example.com {
    reverse_proxy localhost:5000
}
```

---

## Production Considerations

### Security

1. **Change Secret Key:**
   ```bash
   export HOMEPAGE_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   ```

2. **Use Environment Variables:**
   - Never commit `.env` files
   - Use different secrets for each environment
   - Restrict file permissions: `chmod 600 .env`

3. **Firewall Rules:**
   ```bash
   # Only allow localhost access (with reverse proxy)
   sudo ufw allow from 127.0.0.1 to any port 5000
   
   # Or allow specific IP
   sudo ufw allow from YOUR_IP to any port 5000
   ```

4. **Enable HTTPS:**
   - Always use HTTPS in production
   - Use Let's Encrypt for free SSL certificates
   - Configure HSTS headers

### Performance

1. **Enable Caching:**
   ```bash
   export HOMEPAGE_ENABLE_CACHE=True
   export HOMEPAGE_CACHE_TTL=60
   ```

2. **Enable Compression:**
   ```bash
   export HOMEPAGE_ENABLE_COMPRESSION=True
   ```

3. **Use Production WSGI Server:**
   
   For higher performance, use Gunicorn:
   
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   ```
   
   Or uWSGI:
   
   ```bash
   pip install uwsgi
   uwsgi --http 127.0.0.1:5000 --wsgi-file app.py --callable app --processes 4
   ```

### Monitoring

1. **Health Checks:**
   ```bash
   # Add to cron for monitoring
   */5 * * * * curl -f http://localhost:5000/health || echo "Homepage down" | mail -s "Alert" admin@example.com
   ```

2. **Log Rotation:**
   
   Create `/etc/logrotate.d/homepage`:
   ```
   /var/log/homepage/*.log {
       daily
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 www-data www-data
       sharedscripts
   }
   ```

3. **Metrics Collection:**
   ```bash
   # Export metrics periodically
   0 * * * * cd /path/to/homepage && ./venv/bin/python cli.py stats --export /var/log/homepage/metrics-$(date +\%Y\%m\%d-\%H).json
   ```

### Backup

1. **Configuration:**
   ```bash
   # Backup links configuration
   cp links.toml links.toml.backup
   
   # Or use git
   git add links.toml
   git commit -m "Update links"
   git push
   ```

2. **Metrics:**
   ```bash
   # Backup metrics before updates
   python cli.py stats --export backup/metrics-$(date +%Y%m%d).json
   ```

### Updates

1. **Update Process:**
   ```bash
   # Stop service
   systemctl --user stop homepage.service
   
   # Pull updates
   git pull
   
   # Update dependencies
   ./venv/bin/pip install -e . --upgrade
   
   # Restart service
   systemctl --user start homepage.service
   ```

2. **Rollback:**
   ```bash
   # If something goes wrong
   git log --oneline  # Find previous commit
   git checkout COMMIT_HASH
   systemctl --user restart homepage.service
   ```

### Environment-Specific Configs

Development (`.env.development`):
```bash
HOMEPAGE_ENV=development
HOMEPAGE_DEBUG=True
HOMEPAGE_PORT=5000
HOMEPAGE_LOG_LEVEL=DEBUG
HOMEPAGE_ENABLE_CACHE=False
```

Production (`.env.production`):
```bash
HOMEPAGE_ENV=production
HOMEPAGE_DEBUG=False
HOMEPAGE_PORT=5000
HOMEPAGE_LOG_LEVEL=INFO
HOMEPAGE_ENABLE_CACHE=True
HOMEPAGE_ENABLE_COMPRESSION=True
HOMEPAGE_SECRET_KEY=your-secret-key-here
```

Load environment-specific config:
```bash
export $(cat .env.production | xargs)
python app.py
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
journalctl --user -u homepage.service -n 50

# Check if port is in use
sudo lsof -i :5000

# Verify paths in service file
cat ~/.config/systemd/user/homepage.service
```

### Docker Issues

```bash
# View container logs
docker logs homepage

# Check container status
docker ps -a

# Inspect container
docker inspect homepage

# Rebuild without cache
docker build --no-cache -t homepage:latest .
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/homepage

# Fix permissions
chmod 755 /path/to/homepage
chmod 644 /path/to/homepage/*.py
chmod +x /path/to/homepage/venv/bin/*
```

---

## Cloud Deployment

### AWS EC2

1. Launch EC2 instance (t2.micro for small usage)
2. Install Docker or Python
3. Deploy using Docker or systemd
4. Configure security group for port 80/443
5. Use Elastic IP for static address
6. Setup Route53 for DNS

### Digital Ocean

1. Create Droplet
2. Use Docker one-click app
3. Deploy with docker-compose
4. Configure firewall
5. Add domain in DNS settings

### Heroku

Create `Procfile`:
```
web: gunicorn app:app
```

Deploy:
```bash
heroku create your-homepage
git push heroku main
```

### Railway

1. Connect GitHub repository
2. Railway auto-detects Python
3. Add environment variables
4. Deploy automatically on push

---

## Next Steps

After deployment:

1. Test all features work correctly
2. Configure monitoring and alerts
3. Setup regular backups
4. Document your specific configuration
5. Test disaster recovery process
