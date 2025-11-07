"""GeoIP service for determining location from IP addresses."""

import logging
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


class GeoIPService:
    """Service for determining geographic location from IP addresses."""

    @staticmethod
    def get_location(
        ip_address: str | None = None,
        provider: str = "maxmind",
        db_path: str | None = None,
    ) -> tuple[float, float, str]:
        """Get geographic location from IP address.

        Args:
            ip_address: IP address to lookup (None for auto-detection)
            provider: GeoIP provider ('maxmind', 'ipapi', or 'ip-api')
            db_path: Path to MaxMind database file (required for 'maxmind' provider)

        Returns:
            Tuple of (latitude, longitude, location_name)

        Raises:
            ValueError: If provider is invalid or required parameters are missing
            FileNotFoundError: If MaxMind database files not found
            requests.RequestException: If API request fails
        """
        match provider:
            case "maxmind":
                if not db_path:
                    raise ValueError("Database path required for MaxMind provider")
                return _geoip_maxmind(ip_address, db_path)
            case "ipapi":
                return _geoip_ipapi(ip_address)
            case "ip-api":
                return _geoip_ip_api(ip_address)
            case _:
                raise ValueError(f"Invalid GeoIP provider: {provider}")


def _get_asn_info(ip_address: str, asn_db_path: Path) -> str | None:
    """Get ASN organization name for an IP address.

    Args:
        ip_address: IP address to lookup
        asn_db_path: Path to GeoLite2-ASN.mmdb file

    Returns:
        ASN organization name or None if not found
    """
    if not asn_db_path.exists():
        return None

    try:
        import geoip2.database  # pylint: disable=import-outside-toplevel
        import geoip2.errors  # pylint: disable=import-outside-toplevel

        with geoip2.database.Reader(str(asn_db_path)) as asn_reader:
            asn_response = asn_reader.asn(ip_address)
            return asn_response.autonomous_system_organization
    except (geoip2.errors.AddressNotFoundError, AttributeError, ImportError):
        return None


def _geoip_maxmind(ip_address: str | None, db_path: str) -> tuple[float, float, str]:
    """Get location using MaxMind GeoLite2 database.

    Tries databases in order: City -> Country
    Also adds ASN info if available.

    Args:
        ip_address: IP address to lookup (None for auto-detection)
        db_path: Path to GeoLite2-City.mmdb file

    Returns:
        Tuple of (latitude, longitude, location_name)

    Raises:
        FileNotFoundError: If database files not found
    """
    import geoip2.database  # pylint: disable=import-outside-toplevel
    import geoip2.errors  # pylint: disable=import-outside-toplevel

    base_dir = Path(db_path).parent
    city_db = Path(db_path)
    country_db = base_dir / "GeoLite2-Country.mmdb"
    asn_db = base_dir / "GeoLite2-ASN.mmdb"

    # Use a default IP if localhost
    if not ip_address:
        # Fallback: try to get public IP or use a default location
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=3)
            ip_address = response.json()["ip"]
        except (requests.RequestException, KeyError):
            # Ultimate fallback to a central location
            return 52.0, 5.0, "Netherlands"

    # Try City database first (most detailed)
    if city_db.exists():
        try:
            with geoip2.database.Reader(str(city_db)) as reader:
                assert ip_address is not None
                city_response = reader.city(ip_address)

                # Try to get the most specific location name available
                city = (
                    city_response.city.name
                    or (
                        city_response.subdivisions.most_specific.name
                        if city_response.subdivisions
                        else None
                    )
                    or city_response.country.name
                    or "Unknown"
                )

                # Add ASN info if available
                asn_org = _get_asn_info(ip_address, asn_db)
                if asn_org:
                    city = f"{city} ({asn_org})"

                lat = city_response.location.latitude or 0.0
                lon = city_response.location.longitude or 0.0
                return lat, lon, city
        except geoip2.errors.AddressNotFoundError:
            pass  # Try Country database next

    # Fallback to Country database (less detailed, but has coordinates)
    if country_db.exists():
        try:
            with geoip2.database.Reader(str(country_db)) as reader:
                assert ip_address is not None
                country_response = reader.country(ip_address)

                country_name = country_response.country.name or "Unknown"

                # Add ASN info if available
                asn_org = _get_asn_info(ip_address, asn_db)
                if asn_org:
                    country_name = f"{country_name} ({asn_org})"

                # Country database doesn't have coordinates, use approximate center
                # You could maintain a mapping, but for now return generic coordinates
                lat = 52.0  # Approximate European center
                lon = 5.0
                return lat, lon, country_name
        except geoip2.errors.AddressNotFoundError:
            pass

    # No database found or IP not in any database
    raise FileNotFoundError(
        f"MaxMind database not found at {city_db} or {country_db}. "
        "Download from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data"
    )


def _geoip_ipapi(ip_address: str | None) -> tuple[float, float, str]:
    """Get location using ipapi.co (30k requests/month free).

    Args:
        ip_address: IP address to lookup (None for auto-detection)

    Returns:
        Tuple of (latitude, longitude, location_name)

    Raises:
        requests.RequestException: If API request fails
    """
    url = f"https://ipapi.co/{ip_address + '/' if ip_address else ''}json/"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()
    return data["latitude"], data["longitude"], data.get("city", "Unknown")


def _geoip_ip_api(ip_address: str | None) -> tuple[float, float, str]:
    """Get location using ip-api.com (45 requests/minute free).

    Args:
        ip_address: IP address to lookup (None for auto-detection)

    Returns:
        Tuple of (latitude, longitude, location_name)

    Raises:
        requests.RequestException: If API request fails
        ValueError: If API response indicates failure
    """
    url = f"http://ip-api.com/json/{ip_address if ip_address else ''}"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()

    if data["status"] != "success":
        raise ValueError(f"IP-API lookup failed: {data.get('message', 'Unknown error')}")

    return data["lat"], data["lon"], data.get("city", "Unknown")
