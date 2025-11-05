#!/bin/bash
# Setup script for GeoLite2 databases

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CITY_DB="$SCRIPT_DIR/GeoLite2-City.mmdb"
COUNTRY_DB="$SCRIPT_DIR/GeoLite2-Country.mmdb"
ASN_DB="$SCRIPT_DIR/GeoLite2-ASN.mmdb"

echo "🌍 GeoLite2 Database Setup"
echo ""

# Check if databases already exist
existing_dbs=()
[ -f "$CITY_DB" ] && existing_dbs+=("City")
[ -f "$COUNTRY_DB" ] && existing_dbs+=("Country")
[ -f "$ASN_DB" ] && existing_dbs+=("ASN")

if [ ${#existing_dbs[@]} -gt 0 ]; then
    echo "✓ Existing databases found: ${existing_dbs[*]}"
    for db_type in "${existing_dbs[@]}"; do
        case $db_type in
            City) size=$(du -h "$CITY_DB" | cut -f1); echo "  City: $size" ;;
            Country) size=$(du -h "$COUNTRY_DB" | cut -f1); echo "  Country: $size" ;;
            ASN) size=$(du -h "$ASN_DB" | cut -f1); echo "  ASN: $size" ;;
        esac
    done
    echo ""
    read -p "Do you want to replace them? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing databases."
        exit 0
    fi
    rm -f "$CITY_DB" "$COUNTRY_DB" "$ASN_DB"
fi

echo ""
echo "Choose an option:"
echo ""
echo "1) Download test databases (small, limited data, no registration)"
echo "2) Instructions for full databases (requires MaxMind account)"
echo "3) Skip GeoIP setup (use API-based providers instead)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "📥 Downloading MaxMind test databases..."
        echo "   These are small databases with limited data, suitable for testing."
        echo ""
        
        # Download City test database
        echo "Downloading City database..."
        curl -L -o "$CITY_DB" \
            "https://github.com/maxmind/MaxMind-DB/raw/main/test-data/GeoLite2-City-Test.mmdb"
        
        # Download Country test database
        echo "Downloading Country database..."
        curl -L -o "$COUNTRY_DB" \
            "https://github.com/maxmind/MaxMind-DB/raw/main/test-data/GeoLite2-Country-Test.mmdb"
        
        # Download ASN test database
        echo "Downloading ASN database..."
        curl -L -o "$ASN_DB" \
            "https://github.com/maxmind/MaxMind-DB/raw/main/test-data/GeoLite2-ASN-Test.mmdb"
        
        if [ -f "$CITY_DB" ] && [ -f "$COUNTRY_DB" ] && [ -f "$ASN_DB" ]; then
            city_size=$(du -h "$CITY_DB" | cut -f1)
            country_size=$(du -h "$COUNTRY_DB" | cut -f1)
            asn_size=$(du -h "$ASN_DB" | cut -f1)
            echo ""
            echo "✅ Test databases downloaded successfully!"
            echo "   City:    $city_size"
            echo "   Country: $country_size"
            echo "   ASN:     $asn_size"
            echo ""
            echo "⚠️  Note: These test databases have limited IP coverage."
            echo "   For production use, consider option 2 (full databases)."
        else
            echo "❌ Failed to download test databases"
            exit 1
        fi
        ;;
    
    2)
        echo ""
        echo "📚 To download the full GeoLite2 databases:"
        echo ""
        echo "1. Create a free account at: https://www.maxmind.com/en/geolite2/signup"
        echo "2. Generate a license key in your account settings"
        echo "3. Download GeoLite2 databases from:"
        echo "   https://www.maxmind.com/en/accounts/current/geoip/downloads"
        echo ""
        echo "Available databases (all recommended):"
        echo "  • GeoLite2-City.mmdb    - Most detailed, includes coordinates"
        echo "  • GeoLite2-Country.mmdb - Fallback when City lacks data"
        echo "  • GeoLite2-ASN.mmdb     - Adds ISP/organization info"
        echo ""
        echo "4. Extract and copy .mmdb files to:"
        echo "   $SCRIPT_DIR"
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
echo "🧪 Testing databases..."

if command -v python3 &> /dev/null; then
    if ./venv/bin/python3 -c "import geoip2.database; reader = geoip2.database.Reader('$CITY_DB'); response = reader.city('89.160.20.112'); print(f'✓ Test passed: {response.city.name}, {response.country.name}')" 2>/dev/null; then
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "Next steps:"
        echo "1. Enable weather feature in .env:"
        echo "   HOMEPAGE_ENABLE_WEATHER=True"
        echo "2. Set GeoIP provider to maxmind:"
        echo "   HOMEPAGE_GEOIP_PROVIDER=maxmind"
        echo "3. Restart the application"
        echo ""
        echo "ℹ️  The app will automatically use all available databases:"
        echo "   • City (primary) → Country (fallback) → ASN (enrichment)"
    else
        echo "⚠️  Database downloaded but test failed."
        echo "   Make sure geoip2 Python package is installed."
        echo "   The database should still work if geoip2 is available at runtime."
    fi
else
    echo "⚠️  Python not found. Skipping test."
    echo "   The databases should work if geoip2 Python package is installed."
fi

echo ""
