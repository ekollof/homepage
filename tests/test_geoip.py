"""Tests for GeoIP service functionality."""

from unittest.mock import MagicMock, patch

import pytest


class TestGeoIPProviders:
    """Test GeoIP provider implementations."""

    def test_geoip_ipapi_provider(self):
        """Test ipapi provider implementation."""
        from homepage.services.geoip_service import _geoip_ipapi

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "latitude": 52.5,
            "longitude": 13.4,
            "city": "Berlin",
        }

        with patch("requests.get", return_value=mock_response):
            lat, lon, city = _geoip_ipapi("8.8.8.8")
            assert lat == 52.5
            assert lon == 13.4
            assert city == "Berlin"

    def test_geoip_ipapi_provider_none_ip(self):
        """Test ipapi provider with None IP (localhost)."""
        from homepage.services.geoip_service import _geoip_ipapi

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "latitude": 52.5,
            "longitude": 13.4,
            "city": "Berlin",
        }

        with patch("requests.get", return_value=mock_response):
            lat, lon, city = _geoip_ipapi(None)
            assert isinstance(lat, float)
            assert isinstance(lon, float)
            assert isinstance(city, str)

    def test_geoip_ip_api_provider(self):
        """Test ip-api.com provider implementation."""
        from homepage.services.geoip_service import _geoip_ip_api

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "lat": 40.7128,
            "lon": -74.0060,
            "city": "New York",
        }

        with patch("requests.get", return_value=mock_response):
            lat, lon, city = _geoip_ip_api("1.1.1.1")
            assert lat == 40.7128
            assert lon == -74.0060
            assert city == "New York"


class TestGeoIPServiceBasic:
    """Basic GeoIP service tests."""

    def test_get_location_basic(self):
        """Test getting location with basic call."""
        from homepage.services.geoip_service import GeoIPService

        # Test with None IP (localhost) and ipapi provider
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "latitude": 52.0,
                "longitude": 5.0,
                "city": "Amsterdam",
            }
            mock_get.return_value = mock_response

            lat, lon, city = GeoIPService.get_location(ip_address=None, provider="ipapi")
            assert isinstance(lat, float)
            assert isinstance(lon, float)
            assert isinstance(city, str)

    def test_get_location_invalid_provider(self):
        """Test with invalid GeoIP provider."""
        from homepage.services.geoip_service import GeoIPService

        with pytest.raises(ValueError):
            GeoIPService.get_location(ip_address="1.1.1.1", provider="invalid")
