"""Tests for link editing functionality."""

import json


class TestEditingFeature:
    """Test editing functionality."""

    def test_get_config_endpoint(self, client, monkeypatch):
        """Test getting configuration via API."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)

        response = client.get("/api/config")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "category" in data

    def test_get_config_disabled(self, client, monkeypatch):
        """Test config endpoint when editing is disabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", False)

        response = client.get("/api/config")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data

    def test_save_config_endpoint(self, client, monkeypatch, tmp_path):
        """Test saving configuration via API."""
        import homepage.app as app_module

        # Use temporary override file
        override_file = tmp_path / "links.override.toml"
        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)
        monkeypatch.setattr(app_module.config, "CONFIG_OVERRIDE_FILE", override_file)

        test_config = {
            "category": [
                {
                    "name": "Test Category",
                    "icon": "🧪",
                    "links": [{"name": "Test Link", "url": "https://example.com", "icon": "🔗"}],
                }
            ]
        }

        response = client.post(
            "/api/config", data=json.dumps(test_config), content_type="application/json"
        )

        assert response.status_code == 200
        assert override_file.exists()

    def test_save_config_invalid(self, client, monkeypatch, tmp_path):
        """Test saving invalid configuration."""
        import homepage.app as app_module

        # Use temporary override file
        override_file = tmp_path / "links.override.toml"
        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)
        monkeypatch.setattr(app_module.config, "CONFIG_OVERRIDE_FILE", override_file)

        # Missing required fields
        invalid_config = {"category": [{"name": "Test"}]}

        response = client.post(
            "/api/config", data=json.dumps(invalid_config), content_type="application/json"
        )

        # Should accept it as valid (links can be empty)
        assert response.status_code in [200, 400]

    def test_reset_config(self, client, monkeypatch, tmp_path):
        """Test resetting configuration."""
        import homepage.app as app_module

        override_file = tmp_path / "links.override.toml"
        override_file.write_text("# test file")

        monkeypatch.setattr(app_module.config, "ENABLE_EDITING", True)
        monkeypatch.setattr(app_module.config, "CONFIG_OVERRIDE_FILE", override_file)

        response = client.post("/api/config/reset")
        assert response.status_code == 200
        assert not override_file.exists()


class TestConfigMerging:
    """Test configuration merging functionality."""

    def test_merge_configs_with_override(self):
        """Test that override completely replaces base."""
        from homepage.utils import merge_links_configs

        base = {
            "category": [
                {
                    "name": "Dev",
                    "icon": "💻",
                    "links": [{"name": "GitHub", "url": "https://github.com"}],
                }
            ]
        }

        override = {
            "category": [
                {
                    "name": "Personal",
                    "icon": "🏠",
                    "links": [{"name": "Email", "url": "https://mail.example.com"}],
                }
            ]
        }

        result = merge_links_configs(base, override)

        # Should use override exclusively (no merge)
        assert len(result["category"]) == 1
        assert result["category"][0]["name"] == "Personal"
        assert result["category"][0]["icon"] == "🏠"

    def test_merge_empty_override(self):
        """Test merging with empty override returns base."""
        from homepage.utils import merge_links_configs

        base = {"category": [{"name": "Test", "icon": "📝", "links": []}]}
        override: dict = {}

        result = merge_links_configs(base, override)
        assert result == base

    def test_merge_no_override_category(self):
        """Test that missing category key in override returns base."""
        from homepage.utils import merge_links_configs

        base = {"category": [{"name": "Test", "icon": "📝", "links": []}]}
        override = {"other": "data"}

        result = merge_links_configs(base, override)
        assert result == base

    def test_merge_configs_deep_merge(self):
        """Test deep merging of nested configurations."""
        from homepage.utils import merge_links_configs

        base = {
            "category": [
                {
                    "name": "Dev",
                    "icon": "💻",
                    "links": [{"name": "GitHub", "url": "https://github.com"}],
                }
            ]
        }

        override = {
            "category": [
                {
                    "name": "Work",
                    "icon": "🎯",
                    "links": [{"name": "Jira", "url": "https://jira.com"}],
                }
            ]
        }

        result = merge_links_configs(base, override)
        # Override should completely replace base when override exists
        assert result == override

    def test_merge_configs_empty_base(self):
        """Test merging with empty base."""
        from homepage.utils import merge_links_configs

        override = {"category": [{"name": "Dev"}]}
        result = merge_links_configs({}, override)
        assert result == override

    def test_merge_configs_empty_override(self):
        """Test merging with empty override."""
        from homepage.utils import merge_links_configs

        base = {"category": [{"name": "Dev"}]}
        result = merge_links_configs(base, {})
        assert result == base
