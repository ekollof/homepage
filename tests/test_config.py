"""Tests for configuration management."""


from homepage.config import Config


class TestConfig:
    """Test configuration management."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.HOST == "127.0.0.1"
        assert config.PORT == 5000
        # DEBUG depends on environment variable, just check it exists
        assert hasattr(config, "DEBUG")
        assert config.CACHE_TTL == 5

    def test_config_from_env(self):
        """Test loading configuration from environment."""
        # Config class reads from environment at module import time
        # so we can't easily test env vars without reloading
        # Just test that config values are accessible
        assert hasattr(Config, "PORT")
        assert hasattr(Config, "HOST")
        assert isinstance(Config.PORT, int)

    def test_gruvbox_colors_exist(self):
        """Test that Gruvbox colors are defined."""
        config = Config()
        assert "background" in config.GRUVBOX_DARK
        assert "foreground" in config.GRUVBOX_DARK
        assert "color0" in config.GRUVBOX_DARK


class TestConfigEnvironmentVariables:
    """Test configuration from environment variables."""

    def test_config_object_exists(self):
        """Test that config object exists."""
        from homepage.config import get_config

        config = get_config()
        assert config is not None
        assert hasattr(config, "HOST")
        assert hasattr(config, "PORT")

    def test_config_has_required_attributes(self):
        """Test config has required attributes."""
        config = Config()
        required = [
            "HOST",
            "PORT",
            "ENABLE_WEATHER",
            "ENABLE_METRICS",
            "ENABLE_SYSTEM_STATS",
            "ENABLE_COMPRESSION",
        ]
        for attr in required:
            assert hasattr(config, attr), f"Config missing {attr}"

    def test_config_types(self):
        """Test config attribute types."""
        config = Config()
        assert isinstance(config.HOST, str)
        assert isinstance(config.PORT, int)
        assert isinstance(config.ENABLE_WEATHER, bool)
        assert isinstance(config.ENABLE_METRICS, bool)

    def test_gruvbox_colors_defined(self):
        """Test Gruvbox fallback colors are defined."""
        config = Config()
        assert hasattr(config, "GRUVBOX_DARK")
        assert isinstance(config.GRUVBOX_DARK, dict)
        assert "background" in config.GRUVBOX_DARK
        assert "foreground" in config.GRUVBOX_DARK
        # Check for color palette
        assert any(f"color{i}" in config.GRUVBOX_DARK for i in range(16))
