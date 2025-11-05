#!/bin/bash
# Setup script for GeoLite2 database

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_FILE="$SCRIPT_DIR/GeoLite2-City.mmdb"

echo "🌍 GeoLite2 Database Setup"
echo ""

# Check if database already exists
if [ -f "$DB_FILE" ]; then
    echo "✓ GeoLite2 database already exists: $DB_FILE"
    size=$(du -h "$DB_FILE" | cut -f1)
    echo "  Size: $size"
    
    read -p "Do you want to replace it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing database."
        exit 0
    fi
    rm "$DB_FILE"
fi

echo ""
echo "Choose an option:"
echo ""
echo "1) Download test database (small, limited data, no registration)"
echo "2) Instructions for full database (requires MaxMind account)"
echo "3) Skip GeoIP setup (use API-based providers instead)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "📥 Downloading MaxMind test database..."
        echo "   This is a small database with limited data, suitable for testing."
        echo ""
        
        curl -L -o "$DB_FILE" \
            "https://github.com/maxmind/MaxMind-DB/raw/main/test-data/GeoLite2-City-Test.mmdb"
        
        if [ -f "$DB_FILE" ]; then
            size=$(du -h "$DB_FILE" | cut -f1)
            echo ""
            echo "✅ Test database downloaded successfully!"
            echo "   Location: $DB_FILE"
            echo "   Size: $size"
            echo ""
            echo "⚠️  Note: This test database has limited IP coverage."
            echo "   For production use, consider option 2 (full database)."
        else
            echo "❌ Failed to download test database"
            exit 1
        fi
        ;;
    
    2)
        echo ""
        echo "📚 To download the full GeoLite2 database:"
        echo ""
        echo "1. Create a free account at: https://www.maxmind.com/en/geolite2/signup"
        echo "2. Generate a license key in your account settings"
        echo "3. Download GeoLite2-City database from:"
        echo "   https://www.maxmind.com/en/accounts/current/geoip/downloads"
        echo "4. Extract and copy GeoLite2-City.mmdb to:"
        echo "   $DB_FILE"
        echo ""
        echo "Detailed instructions: docs/GEOIP_SETUP.md"
        echo ""
        echo "Or use geoipupdate for automatic updates (recommended)"
        exit 0
        ;;
    
    3)
        echo ""
        echo "📝 To use API-based GeoIP providers instead:"
        echo ""
        echo "Add to your .env file:"
        echo ""
        echo "  # Use ipapi.co (30,000 requests/month free)"
        echo "  HOMEPAGE_GEOIP_PROVIDER=ipapi"
        echo ""
        echo "  # Or use ip-api.com (45 requests/minute free)"
        echo "  HOMEPAGE_GEOIP_PROVIDER=ip-api"
        echo ""
        echo "No database file needed for API providers."
        exit 0
        ;;
    
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Test the database
echo ""
echo "🧪 Testing database..."

if command -v python3 &> /dev/null; then
    if ./venv/bin/python3 -c "import geoip2.database; reader = geoip2.database.Reader('$DB_FILE'); response = reader.city('89.160.20.112'); print(f'✓ Test passed: {response.city.name}, {response.country.name}')" 2>/dev/null; then
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "Next steps:"
        echo "1. Enable weather feature in .env:"
        echo "   HOMEPAGE_ENABLE_WEATHER=True"
        echo "2. Set GeoIP provider to maxmind:"
        echo "   HOMEPAGE_GEOIP_PROVIDER=maxmind"
        echo "3. Restart the application"
    else
        echo "⚠️  Database downloaded but test failed."
        echo "   Make sure geoip2 Python package is installed."
        echo "   The database should still work if geoip2 is available at runtime."
    fi
else
    echo "⚠️  Python not found. Skipping test."
    echo "   The database should work if geoip2 Python package is installed."
fi

echo ""
