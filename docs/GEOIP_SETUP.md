# GeoIP Setup Guide

This guide explains how to set up MaxMind's GeoLite2 database for local IP geolocation.

## Why MaxMind GeoLite2?

- **Fast**: Local database lookups (no external API calls)
- **No Rate Limits**: Unlimited lookups
- **Reliable**: No dependency on external services
- **Privacy**: IP addresses never leave your server
- **Free**: GeoLite2 databases are free to use

### Available Databases

The application supports three GeoLite2 databases:

1. **GeoLite2-City** (Primary) - Most detailed, includes city names and coordinates
2. **GeoLite2-Country** (Fallback) - Used when City database lacks data
3. **GeoLite2-ASN** (Optional) - Adds ISP/organization information

All databases work together automatically when present in the project root.

## Quick Setup

Run the interactive setup script:

```bash
./setup_geoip.sh
```

This will guide you through:
1. **Test databases** - Small databases for testing (no registration needed)
2. **Full databases** - Complete databases with worldwide coverage (requires free MaxMind account)
3. **API providers** - Use online services instead (no database needed)

The script can download all three databases (City, Country, ASN) for comprehensive location data.

## Manual Setup Instructions

### 1. Create a MaxMind Account

1. Go to https://www.maxmind.com/en/geolite2/signup
2. Sign up for a free account
3. Verify your email address

### 2. Generate a License Key

1. Log in to your MaxMind account
2. Navigate to "My License Key" in the left sidebar
3. Click "Generate New License Key"
4. Give it a description (e.g., "Homepage App")
5. Select "No" for "Will this key be used for GeoIP Update?"
6. Click "Confirm"
7. **Save your license key** - you won't be able to see it again!

### 3. Download GeoLite2-City Database

#### Option A: Test Databases (Quick Start)

For testing and development, you can use the small test databases:

```bash
# Download City database
curl -L -o GeoLite2-City.mmdb \
  "https://github.com/maxmind/MaxMind-DB/raw/main/test-data/GeoLite2-City-Test.mmdb"

# Download Country database (optional, for fallback)
curl -L -o GeoLite2-Country.mmdb \
  "https://github.com/maxmind/MaxMind-DB/raw/main/test-data/GeoLite2-Country-Test.mmdb"

# Download ASN database (optional, for ISP info)
curl -L -o GeoLite2-ASN.mmdb \
  "https://github.com/maxmind/MaxMind-DB/raw/main/test-data/GeoLite2-ASN-Test.mmdb"
```

**Note**: The test databases have limited IP coverage (only a few test IPs). For production use, download the full databases (Option B).

#### Option B: Full Databases (Direct Download)

1. Go to https://www.maxmind.com/en/accounts/current/geoip/downloads
2. Find the databases you want to download:
   - **GeoLite2 City** (Recommended) - Most detailed
   - **GeoLite2 Country** (Recommended) - Fallback for missing City data
   - **GeoLite2 ASN** (Optional) - Adds ISP/organization info
3. Click "Download GZIP" for the binary format (.mmdb)
4. Extract the `.tar.gz` file
5. Copy `GeoLite2-*.mmdb` files to your homepage directory

```bash
cd ~/devel/homepage

# Extract City database
tar -xzf ~/Downloads/GeoLite2-City_*.tar.gz
cp GeoLite2-City_*/GeoLite2-City.mmdb .

# Extract Country database (optional but recommended)
tar -xzf ~/Downloads/GeoLite2-Country_*.tar.gz
cp GeoLite2-Country_*/GeoLite2-Country.mmdb .

# Extract ASN database (optional)
tar -xzf ~/Downloads/GeoLite2-ASN_*.tar.gz
cp GeoLite2-ASN_*/GeoLite2-ASN.mmdb .
```

#### Option C: Using geoipupdate (Automatic Updates)

Install geoipupdate:

**Ubuntu/Debian:**
```bash
sudo add-apt-repository ppa:maxmind/ppa
sudo apt update
sudo apt install geoipupdate
```

**Arch Linux:**
```bash
sudo pacman -S geoipupdate
```

**macOS:**
```bash
brew install geoipupdate
```

Configure geoipupdate:

Edit `/etc/GeoIP.conf`:

```conf
AccountID YOUR_ACCOUNT_ID
LicenseKey YOUR_LICENSE_KEY
EditionIDs GeoLite2-City
DatabaseDirectory /home/ekollof/devel/homepage
```

Run the update:

```bash
sudo geoipupdate
```

Set up automatic updates (optional):

```bash
# Add to crontab
sudo crontab -e

# Add this line to update weekly on Sundays at 2 AM
0 2 * * 0 /usr/bin/geoipupdate
```

### 4. Configure Homepage

Update your `.env` file:

```bash
# Use MaxMind for GeoIP
HOMEPAGE_GEOIP_PROVIDER=maxmind

# Optional: Specify custom path (defaults to ./GeoLite2-City.mmdb)
HOMEPAGE_GEOIP_DB_PATH=/home/ekollof/devel/homepage/GeoLite2-City.mmdb
```

### 5. Restart the Application

```bash
# If using systemd
sudo systemctl restart homepage

# Or if running directly
pkill -f "python.*app.py"
python app.py
```

## Fallback Options

If you don't want to use MaxMind, you can use the API-based providers:

```bash
# Use ipapi.co (30,000 requests/month free)
HOMEPAGE_GEOIP_PROVIDER=ipapi

# Or use ip-api.com (45 requests/minute free)
HOMEPAGE_GEOIP_PROVIDER=ip-api
```

## Testing

Test the GeoIP functionality:

```bash
curl http://localhost:5000/api/weather
```

You should see weather data with your location automatically detected.

## Database Updates

MaxMind updates the GeoLite2 databases on the first Tuesday of each month. To stay current:

- **Manual**: Re-download the database monthly
- **Automatic**: Use geoipupdate with a cron job (recommended)

## Troubleshooting

### "MaxMind database not found"

Make sure the database file exists:

```bash
ls -lh GeoLite2-City.mmdb
```

If not found, check the path in your `.env` file.

### "IP address not found in GeoIP database"

This happens with:
- Private IP addresses (127.0.0.1, 192.168.x.x, etc.)
- Very new IP addresses not yet in the database

The app will fall back to a default location or try to get your public IP.

### Permission denied

Make sure the database file is readable:

```bash
chmod 644 GeoLite2-City.mmdb
```

## License

GeoLite2 databases are distributed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).

This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.
