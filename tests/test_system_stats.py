"""Tests for system stats and power management functionality."""

import platform
from unittest.mock import MagicMock, patch

import pytest


class TestSystemStats:
    """Test system stats API endpoint."""

    def test_system_stats_enabled(self, client, monkeypatch):
        """Test /api/system-stats returns data when feature is enabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        response = client.get("/api/system-stats")
        assert response.status_code == 200
        data = response.get_json()

        # Check required fields are present
        assert "cpu_percent" in data
        assert "cpu_count" in data
        assert "cpu_freq_current" in data
        assert "memory_percent" in data
        assert "memory_used_mb" in data
        assert "memory_total_mb" in data
        assert "disk_percent" in data
        assert "disk_used_gb" in data
        assert "disk_total_gb" in data
        assert "network_sent_mb" in data
        assert "network_recv_mb" in data
        assert "processes" in data
        assert "uptime_seconds" in data

        # Check data types and ranges
        assert isinstance(data["cpu_percent"], (int, float))
        assert 0 <= data["cpu_percent"] <= 100
        assert isinstance(data["cpu_count"], int)
        assert data["cpu_count"] > 0
        assert isinstance(data["memory_percent"], (int, float))
        assert 0 <= data["memory_percent"] <= 100
        assert isinstance(data["processes"], int)
        assert data["processes"] > 0
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0

    def test_system_stats_disabled(self, client, monkeypatch):
        """Test /api/system-stats returns 404 when feature is disabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", False)

        response = client.get("/api/system-stats")
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data

    def test_system_stats_battery_conditional(self, client, monkeypatch):
        """Test battery data is only present when available."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        response = client.get("/api/system-stats")
        assert response.status_code == 200
        data = response.get_json()

        # Battery data is optional
        if "battery" in data:
            assert "percent" in data["battery"]
            assert "plugged" in data["battery"]
            assert isinstance(data["battery"]["percent"], (int, float))
            assert 0 <= data["battery"]["percent"] <= 100
            assert isinstance(data["battery"]["plugged"], bool)

    def test_system_stats_temperature_conditional(self, client, monkeypatch):
        """Test temperature data is only present when available."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        response = client.get("/api/system-stats")
        assert response.status_code == 200
        data = response.get_json()

        # Temperature data is optional
        if "temperature_avg" in data:
            assert isinstance(data["temperature_avg"], (int, float))
            # Reasonable temperature range (Celsius)
            assert -50 <= data["temperature_avg"] <= 150

    def test_system_stats_network_counters(self, client, monkeypatch):
        """Test network counters are reasonable values."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        response = client.get("/api/system-stats")
        assert response.status_code == 200
        data = response.get_json()

        # Network I/O should be non-negative
        assert data["network_sent_mb"] >= 0
        assert data["network_recv_mb"] >= 0

    def test_system_stats_error_handling(self, client, monkeypatch):
        """Test system stats handles psutil errors gracefully."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        # Mock psutil to raise an exception
        with patch("psutil.cpu_percent", side_effect=Exception("Test error")):
            response = client.get("/api/system-stats")
            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data
            assert "Failed to fetch system stats" in data["error"]


class TestCPUGovernors:
    """Test CPU governor functionality (Linux only)."""

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_get_cpu_governors_linux(self, monkeypatch):
        """Test getting CPU governors on Linux."""
        from homepage.services.system_stats_service import SystemStatsService

        # Mock sysfs file reading
        mock_files = {
            "/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors": (
                "powersave performance"
            ),
            "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor": "powersave",
        }

        def mock_read(path):
            if path in mock_files:
                return mock_files[path]
            return None

        monkeypatch.setattr(SystemStatsService, "_read_sysfs_file", staticmethod(mock_read))

        with patch("psutil.cpu_count", return_value=1):
            result = SystemStatsService.get_cpu_governors()

        assert result["available"] is True
        assert "cpus" in result
        assert len(result["cpus"]) == 1
        assert result["cpus"][0]["governor"] == "powersave"
        assert "powersave" in result["cpus"][0]["available_governors"]

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_set_cpu_governor_success(self, monkeypatch):
        """Test setting CPU governor successfully."""
        from homepage.services.system_stats_service import SystemStatsService

        # Mock privilege escalation finding
        def mock_which(cmd):
            return "/usr/bin/sudo" if cmd == "sudo" else None

        # Mock successful subprocess run
        class MockResult:
            returncode = 0
            stdout = "Successfully set governor to performance for all 16 CPUs"
            stderr = ""

        def mock_run(*args, **kwargs):
            return MockResult()

        monkeypatch.setattr("shutil.which", mock_which)
        monkeypatch.setattr("subprocess.run", mock_run)

        result = SystemStatsService.set_cpu_governor("performance")

        assert result["success"] is True
        assert "performance" in result["message"]

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_set_cpu_governor_partial_failure(self, monkeypatch):
        """Test setting CPU governor with partial failure."""
        from homepage.services.system_stats_service import SystemStatsService

        # Mock privilege escalation finding
        def mock_which(cmd):
            return "/usr/bin/sudo" if cmd == "sudo" else None

        # Mock failed subprocess run (non-zero exit code)
        class MockResult:
            returncode = 1
            stdout = ""
            stderr = "Warning: Set governor for 1/2 CPUs"

        def mock_run(*args, **kwargs):
            return MockResult()

        monkeypatch.setattr("shutil.which", mock_which)
        monkeypatch.setattr("subprocess.run", mock_run)

        result = SystemStatsService.set_cpu_governor("performance")

        assert result["success"] is False
        assert "1/2" in result["message"]

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_set_cpu_governor_all_failure(self, monkeypatch):
        """Test setting CPU governor with all writes failing."""
        from homepage.services.system_stats_service import SystemStatsService

        # Mock privilege escalation finding
        def mock_which(cmd):
            return "/usr/bin/sudo" if cmd == "sudo" else None

        # Mock completely failed subprocess run
        class MockResult:
            returncode = 1
            stdout = ""
            stderr = "Error: Failed to set governor (no CPUs updated)"

        def mock_run(*args, **kwargs):
            return MockResult()

        monkeypatch.setattr("shutil.which", mock_which)
        monkeypatch.setattr("subprocess.run", mock_run)

        result = SystemStatsService.set_cpu_governor("performance")

        assert result["success"] is False
        assert "Failed to set governor" in result["message"]

    @pytest.mark.skipif(platform.system() == "Linux", reason="Non-Linux only")
    def test_get_cpu_governors_non_linux(self):
        """Test that CPU governors return not available on non-Linux."""
        from homepage.services.system_stats_service import SystemStatsService

        result = SystemStatsService.get_cpu_governors()
        assert result["available"] is False
        assert result["reason"] == "Not Linux"

    @pytest.mark.skipif(platform.system() == "Linux", reason="Non-Linux only")
    def test_set_cpu_governor_non_linux(self):
        """Test that setting CPU governor fails on non-Linux."""
        from homepage.services.system_stats_service import SystemStatsService

        result = SystemStatsService.set_cpu_governor("performance")
        assert result["success"] is False
        assert result["message"] == "Not Linux"

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_get_cpu_governors_power_saving_detection(self, monkeypatch):
        """Test power saving is detected when using power save governors."""
        from homepage.services.system_stats_service import SystemStatsService

        def mock_read(path):
            if "scaling_available_governors" in path:
                return "powersave performance conservative"
            elif "scaling_governor" in path:
                return "conservative"
            return None

        monkeypatch.setattr(SystemStatsService, "_read_sysfs_file", staticmethod(mock_read))

        with patch("psutil.cpu_count", return_value=1):
            result = SystemStatsService.get_cpu_governors()

        assert result["power_saving_enabled"] is True

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_get_cpu_governors_performance_detection(self, monkeypatch):
        """Test power saving is disabled when using performance governor."""
        from homepage.services.system_stats_service import SystemStatsService

        def mock_read(path):
            if "scaling_available_governors" in path:
                return "powersave performance"
            elif "scaling_governor" in path:
                return "performance"
            return None

        monkeypatch.setattr(SystemStatsService, "_read_sysfs_file", staticmethod(mock_read))

        with patch("psutil.cpu_count", return_value=1):
            result = SystemStatsService.get_cpu_governors()

        assert result["power_saving_enabled"] is False


class TestIOSchedulers:
    """Test I/O scheduler functionality (Linux only)."""

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_get_io_schedulers_linux(self, monkeypatch):
        """Test getting I/O schedulers on Linux."""
        from homepage.services.system_stats_service import SystemStatsService

        # This test mainly checks that the function handles the Linux case
        # and doesn't crash. Full functional testing requires real sysfs.
        result = SystemStatsService.get_io_schedulers()

        # Should return a dict with 'available' key
        assert isinstance(result, dict)
        assert "available" in result
        # Result should be a boolean
        assert isinstance(result["available"], bool)

        # If it's available, should have devices key
        if result["available"]:
            assert "devices" in result
            assert isinstance(result["devices"], list)

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_get_io_schedulers_parsing(self, monkeypatch):
        """Test parsing of I/O scheduler output."""

        # Test the scheduler data parsing directly
        test_cases = [
            ("noop deadline [cfq]", ["noop", "deadline", "cfq"], "cfq"),
            ("none kyber [mq-deadline]", ["none", "kyber", "mq-deadline"], "mq-deadline"),
        ]

        for scheduler_string, expected_available, expected_current in test_cases:
            # Parse like the actual code does
            available = scheduler_string.replace("[", "").replace("]", "").split()
            current = None
            for sched in scheduler_string.split():
                if sched.startswith("[") and sched.endswith("]"):
                    current = sched[1:-1]
                    break

            assert available == expected_available
            assert current == expected_current

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_set_io_scheduler_success(self, monkeypatch):
        """Test setting I/O scheduler successfully."""
        from homepage.services.system_stats_service import SystemStatsService

        # Mock privilege escalation finding
        def mock_which(cmd):
            return "/usr/bin/sudo" if cmd == "sudo" else None

        # Mock successful subprocess run
        class MockResult:
            returncode = 0
            stdout = "I/O scheduler for sda set to deadline"
            stderr = ""

        def mock_run(*args, **kwargs):
            return MockResult()

        monkeypatch.setattr("shutil.which", mock_which)
        monkeypatch.setattr("subprocess.run", mock_run)

        result = SystemStatsService.set_io_scheduler("sda", "deadline")

        assert result["success"] is True
        assert "deadline" in result["message"]
        assert "sda" in result["message"]

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_set_io_scheduler_failure(self, monkeypatch):
        """Test setting I/O scheduler with failure."""
        from homepage.services.system_stats_service import SystemStatsService

        # Mock privilege escalation finding
        def mock_which(cmd):
            return "/usr/bin/sudo" if cmd == "sudo" else None

        # Mock failed subprocess run
        class MockResult:
            returncode = 1
            stdout = ""
            stderr = "Error: Failed to set I/O scheduler"

        def mock_run(*args, **kwargs):
            return MockResult()

        monkeypatch.setattr("shutil.which", mock_which)
        monkeypatch.setattr("subprocess.run", mock_run)

        result = SystemStatsService.set_io_scheduler("sda", "deadline")

        assert result["success"] is False
        assert "Failed to set I/O scheduler" in result["message"]

    @pytest.mark.skipif(platform.system() == "Linux", reason="Non-Linux only")
    def test_get_io_schedulers_non_linux(self):
        """Test that I/O schedulers return not available on non-Linux."""
        from homepage.services.system_stats_service import SystemStatsService

        result = SystemStatsService.get_io_schedulers()
        assert result["available"] is False
        assert result["reason"] == "Not Linux"

    @pytest.mark.skipif(platform.system() == "Linux", reason="Non-Linux only")
    def test_set_io_scheduler_non_linux(self):
        """Test that setting I/O scheduler fails on non-Linux."""
        from homepage.services.system_stats_service import SystemStatsService

        result = SystemStatsService.set_io_scheduler("sda", "deadline")
        assert result["success"] is False
        assert result["message"] == "Not Linux"


class TestPowerManagementAPI:
    """Test Power Management API routes."""

    def test_set_cpu_governor_api_success(self, client, monkeypatch):
        """Test POST /api/system-stats/cpu-governor with success."""
        import homepage.app as app_module
        from homepage.services.system_stats_service import SystemStatsService

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        def mock_set_governor(governor):
            if governor in ["performance", "powersave"]:
                return {"success": True, "message": f"Set to {governor}"}
            return {"success": False, "message": "Unknown governor"}

        monkeypatch.setattr(SystemStatsService, "set_cpu_governor", staticmethod(mock_set_governor))

        response = client.post(
            "/api/system-stats/cpu-governor",
            json={"governor": "performance"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_set_cpu_governor_api_missing_parameter(self, client, monkeypatch):
        """Test POST /api/system-stats/cpu-governor with missing parameter."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        response = client.post(
            "/api/system-stats/cpu-governor",
            json={},
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_set_cpu_governor_api_disabled(self, client, monkeypatch):
        """Test POST /api/system-stats/cpu-governor when feature is disabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", False)

        response = client.post(
            "/api/system-stats/cpu-governor",
            json={"governor": "performance"},
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_set_io_scheduler_api_success(self, client, monkeypatch):
        """Test POST /api/system-stats/io-scheduler with success."""
        import homepage.app as app_module
        from homepage.services.system_stats_service import SystemStatsService

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        def mock_set_scheduler(device, scheduler):
            if device in ["sda", "nvme0n1"] and scheduler in ["noop", "deadline", "cfq"]:
                return {"success": True, "message": f"Set {device} to {scheduler}"}
            return {"success": False, "message": "Invalid device or scheduler"}

        monkeypatch.setattr(
            SystemStatsService, "set_io_scheduler", staticmethod(mock_set_scheduler)
        )

        response = client.post(
            "/api/system-stats/io-scheduler",
            json={"device": "sda", "scheduler": "deadline"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_set_io_scheduler_api_missing_device(self, client, monkeypatch):
        """Test POST /api/system-stats/io-scheduler with missing device."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        response = client.post(
            "/api/system-stats/io-scheduler",
            json={"scheduler": "deadline"},
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_set_io_scheduler_api_missing_scheduler(self, client, monkeypatch):
        """Test POST /api/system-stats/io-scheduler with missing scheduler."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        response = client.post(
            "/api/system-stats/io-scheduler",
            json={"device": "sda"},
            content_type="application/json",
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_set_io_scheduler_api_disabled(self, client, monkeypatch):
        """Test POST /api/system-stats/io-scheduler when feature is disabled."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", False)

        response = client.post(
            "/api/system-stats/io-scheduler",
            json={"device": "sda", "scheduler": "deadline"},
            content_type="application/json",
        )

        assert response.status_code == 404


class TestPowerManagementIntegration:
    """Test power management integration with system stats."""

    @pytest.mark.skipif(platform.system() != "Linux", reason="Linux only")
    def test_system_stats_includes_power_management_linux(self, client, monkeypatch):
        """Test that system stats includes power management on Linux."""
        import homepage.app as app_module
        from homepage.services.system_stats_service import SystemStatsService

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        # Mock governors and schedulers
        def mock_read(path):
            if "scaling_available_governors" in path:
                return "powersave performance"
            elif "scaling_governor" in path:
                return "powersave"
            elif "queue/scheduler" in path:
                return "noop deadline [cfq]"
            return None

        monkeypatch.setattr(SystemStatsService, "_read_sysfs_file", staticmethod(mock_read))

        with patch("psutil.cpu_percent", return_value=10.5):
            with patch("psutil.cpu_count", return_value=4):
                with patch("psutil.cpu_freq", return_value=MagicMock(current=2400, max=3600)):
                    with patch("psutil.virtual_memory") as mock_mem:
                        mock_mem.return_value = MagicMock(
                            percent=50, used=2e9, total=4e9, available=2e9
                        )
                        with patch("psutil.disk_usage") as mock_disk:
                            mock_disk.return_value = MagicMock(
                                percent=30, used=100e9, total=500e9, free=400e9
                            )
                            with patch("psutil.net_io_counters") as mock_net:
                                mock_net.return_value = MagicMock(bytes_sent=1e9, bytes_recv=2e9)
                                with patch("psutil.pids", return_value=list(range(100))):
                                    with patch("psutil.boot_time", return_value=0):
                                        with patch("pathlib.Path.exists", return_value=True):
                                            with patch(
                                                "pathlib.Path.iterdir",
                                                return_value=iter([]),
                                            ):
                                                response = client.get("/api/system-stats")

        assert response.status_code == 200
        data = response.get_json()

        # Check that power_management is in the response
        assert "power_management" in data
        assert "governors" in data["power_management"]
        assert data["power_management"]["governors"]["available"] is True

    @pytest.mark.skipif(platform.system() in ("Linux", "FreeBSD"), reason="Non-Linux/FreeBSD only")
    def test_system_stats_excludes_power_management_non_linux(self, client, monkeypatch):
        """Test that system stats excludes power management on non-Linux/FreeBSD systems."""
        import homepage.app as app_module

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        with patch("psutil.cpu_percent", return_value=10.5):
            with patch("psutil.cpu_count", return_value=4):
                with patch("psutil.cpu_freq", return_value=MagicMock(current=2400, max=3600)):
                    with patch("psutil.virtual_memory") as mock_mem:
                        mock_mem.return_value = MagicMock(
                            percent=50, used=2e9, total=4e9, available=2e9
                        )
                        with patch("psutil.disk_usage") as mock_disk:
                            mock_disk.return_value = MagicMock(
                                percent=30, used=100e9, total=500e9, free=400e9
                            )
                            with patch("psutil.net_io_counters") as mock_net:
                                mock_net.return_value = MagicMock(bytes_sent=1e9, bytes_recv=2e9)
                                with patch("psutil.pids", return_value=list(range(100))):
                                    with patch("psutil.boot_time", return_value=0):
                                        response = client.get("/api/system-stats")

        assert response.status_code == 200
        data = response.get_json()

        # Power management should NOT be present on non-Linux/FreeBSD systems
        assert "power_management" not in data


class TestZFSStats:
    """Test ZFS statistics functionality."""

    def test_zfs_stats_available_with_zfs(self, monkeypatch):
        """Test ZFS stats when ZFS is available."""
        from homepage.services.system_stats_service import SystemStatsService

        # Mock sysctl to return ZFS data
        def mock_read_sysctl(name):
            sysctl_values = {
                "kstat.zfs.misc.arcstats.size": "10737418240",  # 10GB
                "kstat.zfs.misc.arcstats.c_max": "21474836480",  # 20GB
                "kstat.zfs.misc.arcstats.hits": "1000000",
                "kstat.zfs.misc.arcstats.misses": "10000",
            }
            return sysctl_values.get(name)

        monkeypatch.setattr(SystemStatsService, "_read_sysctl", mock_read_sysctl)
        monkeypatch.setattr(SystemStatsService, "_is_zfs_available", lambda: True)

        # Mock zpool list command
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "tank\tONLINE\t500G\t100G\t400G\n"

        with patch("subprocess.run", return_value=mock_result):
            stats = SystemStatsService.get_zfs_stats()

        assert stats["available"] is True
        assert "arc" in stats
        assert stats["arc"]["size_mb"] == 10240.0
        assert stats["arc"]["max_mb"] == 20480.0
        assert stats["arc"]["size_percent"] == 50.0
        assert stats["arc"]["hit_ratio"] == 99.0  # 1000000/(1000000+10000)
        assert "pools" in stats
        assert len(stats["pools"]) == 1
        assert stats["pools"][0]["name"] == "tank"
        assert stats["pools"][0]["health"] == "ONLINE"

    def test_zfs_stats_not_available(self, monkeypatch):
        """Test ZFS stats when ZFS is not available."""
        from homepage.services.system_stats_service import SystemStatsService

        monkeypatch.setattr(SystemStatsService, "_is_zfs_available", lambda: False)

        stats = SystemStatsService.get_zfs_stats()

        assert stats["available"] is False
        assert stats["reason"] == "ZFS not loaded"

    def test_zfs_in_system_stats_response(self, client, monkeypatch):
        """Test that ZFS stats appear in system stats API when available."""
        import homepage.app as app_module
        from homepage.services.system_stats_service import SystemStatsService

        monkeypatch.setattr(app_module.config, "ENABLE_SYSTEM_STATS", True)

        # Mock ZFS stats
        mock_zfs_stats = {
            "available": True,
            "arc": {
                "size_mb": 8192.0,
                "max_mb": 16384.0,
                "size_percent": 50.0,
                "hit_ratio": 99.5,
                "hits": 1000000,
                "misses": 5000,
            },
            "pools": [
                {
                    "name": "tank",
                    "health": "ONLINE",
                    "size": "1T",
                    "allocated": "500G",
                    "free": "500G",
                }
            ],
        }

        monkeypatch.setattr(SystemStatsService, "get_zfs_stats", lambda: mock_zfs_stats)

        with patch("psutil.cpu_percent", return_value=10.0):
            with patch("psutil.cpu_count", return_value=4):
                with patch("psutil.cpu_freq", return_value=None):
                    with patch("psutil.virtual_memory") as mock_mem:
                        mock_mem.return_value = MagicMock(
                            percent=50, used=2e9, total=4e9, available=2e9
                        )
                        with patch("psutil.disk_usage") as mock_disk:
                            mock_disk.return_value = MagicMock(
                                percent=30, used=100e9, total=500e9, free=400e9
                            )
                            with patch("psutil.net_io_counters") as mock_net:
                                mock_net.return_value = MagicMock(bytes_sent=1e9, bytes_recv=2e9)
                                with patch("psutil.pids", return_value=list(range(100))):
                                    with patch("psutil.boot_time", return_value=0):
                                        response = client.get("/api/system-stats")

        assert response.status_code == 200
        data = response.get_json()

        # Check ZFS stats are present
        assert "zfs" in data
        assert data["zfs"]["available"] is True
        assert data["zfs"]["arc"]["hit_ratio"] == 99.5
        assert len(data["zfs"]["pools"]) == 1
