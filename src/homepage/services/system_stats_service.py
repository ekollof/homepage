"""System statistics service."""

import logging
import platform
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class SystemStatsService:
    """Service for collecting system statistics."""

    # Class variable to store last network I/O reading for rate calculation
    _last_net_io = None
    _last_net_time = None

    @staticmethod
    def _is_linux() -> bool:
        """Check if running on Linux."""
        return platform.system() == "Linux"

    @staticmethod
    def _read_sysfs_file(path: str) -> str | None:
        """Safely read a sysfs file."""
        try:
            return Path(path).read_text().strip()
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.debug("Failed to read %s: %s", path, e)
            return None

    @staticmethod
    def _write_sysfs_file(path: str, value: str) -> bool:
        """Safely write to a sysfs file."""
        try:
            Path(path).write_text(value)
            return True
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error("Failed to write to %s: %s", path, e)
            return False

    @staticmethod
    def get_cpu_governors() -> dict:
        """Get available and current CPU governors (Linux only).

        Returns:
            Dictionary with available governors, current governor per CPU,
            and whether power saving is enabled.
        """
        if not SystemStatsService._is_linux():
            return {"available": False, "reason": "Not Linux"}

        try:
            import psutil  # pylint: disable=import-outside-toplevel

            cpu_count = psutil.cpu_count()
            if cpu_count is None:
                return {"available": False, "reason": "Could not determine CPU count"}

            governors_info: dict[str, bool | list | str | None] = {
                "available": True,
                "cpus": [],
                "power_saving_enabled": False,
            }

            # Check each CPU
            for cpu in range(cpu_count):
                cpu_info: dict[str, int | str | list[str]] = {"cpu": cpu}

                # Get available governors
                available_path = (
                    f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_available_governors"
                )
                available = SystemStatsService._read_sysfs_file(available_path)
                if available:
                    cpu_info["available_governors"] = available.split()

                # Get current governor
                governor_path = f"/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor"
                governor = SystemStatsService._read_sysfs_file(governor_path)
                if governor:
                    cpu_info["governor"] = governor
                    # Power saving governors
                    if governor in ["powersave", "conservative"]:
                        governors_info["power_saving_enabled"] = True

                governors_info["cpus"].append(cpu_info)  # type: ignore[union-attr]

            # If all CPUs have same governor, simplify
            cpus_list = governors_info["cpus"]
            if isinstance(cpus_list, list):
                governors = [
                    cpu.get("governor") if isinstance(cpu, dict) else None for cpu in cpus_list
                ]
                if governors and all(g == governors[0] for g in governors):
                    governors_info["current_governor"] = governors[0]
                    # Simplify to just show one set of available governors
                    if cpus_list and isinstance(cpus_list[0], dict):
                        governors_info["available_governors"] = cpus_list[0].get(
                            "available_governors", []
                        )

            return governors_info

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to get CPU governors: %s", e)
            return {"available": False, "reason": str(e)}

    @staticmethod
    def _find_privilege_escalator() -> str | None:
        """Find available privilege escalation tool (pkexec, sudo, or doas).

        Returns:
            Command to use for privilege escalation, or None if none found
        """
        import shutil  # pylint: disable=import-outside-toplevel

        # Try pkexec first (best for GUI apps, no password prompt if policy allows)
        if shutil.which("pkexec"):
            return "pkexec"
        # Then sudo
        if shutil.which("sudo"):
            return "sudo"
        # Finally doas
        if shutil.which("doas"):
            return "doas"

        return None

    @staticmethod
    def set_cpu_governor(governor: str) -> dict:
        """Set CPU governor for all CPUs (Linux only).

        Args:
            governor: Governor name (e.g., 'performance', 'powersave')

        Returns:
            Dictionary with success status and message
        """
        if not SystemStatsService._is_linux():
            return {"success": False, "message": "Not Linux"}

        try:
            import subprocess  # pylint: disable=import-outside-toplevel
            from pathlib import Path  # pylint: disable=import-outside-toplevel

            # Find privilege escalation tool
            escalator = SystemStatsService._find_privilege_escalator()
            if not escalator:
                return {
                    "success": False,
                    "message": (
                        "No privilege escalation tool found " "(pkexec, sudo, or doas required)"
                    ),
                }

            # Get path to helper script
            helper_script = (
                Path(__file__).parent.parent.parent.parent / "scripts" / "power-mgmt-helper.sh"
            )
            if not helper_script.exists():
                return {
                    "success": False,
                    "message": f"Helper script not found: {helper_script}",
                }

            # Execute helper script with privilege escalation
            cmd = [escalator, str(helper_script), "set-governor", governor]

            # Add non-interactive flag for sudo
            if escalator == "sudo":
                cmd = ["sudo", "-n", str(helper_script), "set-governor", governor]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                env={"PATH": "/usr/bin:/bin:/usr/local/bin"},  # Clean environment
            )

            if result.returncode == 0:
                return {"success": True, "message": result.stdout.strip()}
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return {"success": False, "message": error_msg or "Failed to set governor"}

        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Operation timed out (30s limit)"}
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to set CPU governor: %s", e)
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_io_schedulers() -> dict:
        """Get available and current I/O schedulers (Linux only).

        Returns:
            Dictionary with scheduler info per block device
        """
        if not SystemStatsService._is_linux():
            return {"available": False, "reason": "Not Linux"}

        try:
            schedulers_info = {"available": True, "devices": []}

            # Check common block devices
            sys_block = Path("/sys/block")
            if not sys_block.exists():
                return {"available": False, "reason": "/sys/block not found"}

            for device_path in sorted(sys_block.iterdir()):
                device_name = device_path.name
                # Skip loop devices, ram devices, etc.
                if device_name.startswith(("loop", "ram")):
                    continue

                scheduler_path = device_path / "queue" / "scheduler"
                scheduler_data = SystemStatsService._read_sysfs_file(str(scheduler_path))

                if scheduler_data:
                    # Parse scheduler format: "noop deadline [cfq]"
                    available = scheduler_data.replace("[", "").replace("]", "").split()
                    current = None
                    for sched in scheduler_data.split():
                        if sched.startswith("[") and sched.endswith("]"):
                            current = sched[1:-1]
                            break

                    schedulers_info["devices"].append(
                        {
                            "device": device_name,
                            "current_scheduler": current,
                            "available_schedulers": available,
                        }
                    )

            return schedulers_info

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to get I/O schedulers: %s", e)
            return {"available": False, "reason": str(e)}

    @staticmethod
    def set_io_scheduler(device: str, scheduler: str) -> dict:
        """Set I/O scheduler for a block device (Linux only).

        Args:
            device: Device name (e.g., 'sda', 'nvme0n1')
            scheduler: Scheduler name (e.g., 'deadline', 'cfq', 'noop')

        Returns:
            Dictionary with success status and message
        """
        if not SystemStatsService._is_linux():
            return {"success": False, "message": "Not Linux"}

        try:
            import subprocess  # pylint: disable=import-outside-toplevel
            from pathlib import Path  # pylint: disable=import-outside-toplevel

            # Find privilege escalation tool
            escalator = SystemStatsService._find_privilege_escalator()
            if not escalator:
                return {
                    "success": False,
                    "message": (
                        "No privilege escalation tool found " "(pkexec, sudo, or doas required)"
                    ),
                }

            # Get path to helper script
            helper_script = (
                Path(__file__).parent.parent.parent.parent / "scripts" / "power-mgmt-helper.sh"
            )
            if not helper_script.exists():
                return {
                    "success": False,
                    "message": f"Helper script not found: {helper_script}",
                }

            # Execute helper script with privilege escalation
            cmd = [escalator, str(helper_script), "set-scheduler", device, scheduler]

            # Add non-interactive flag for sudo
            if escalator == "sudo":
                cmd = ["sudo", "-n", str(helper_script), "set-scheduler", device, scheduler]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                env={"PATH": "/usr/bin:/bin:/usr/local/bin"},  # Clean environment
            )

            if result.returncode == 0:
                return {"success": True, "message": result.stdout.strip()}
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return {"success": False, "message": error_msg or "Failed to set scheduler"}

        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Operation timed out (30s limit)"}
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to set I/O scheduler: %s", e)
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_stats() -> dict:
        """Get real-time system statistics.

        Returns:
            Dictionary with CPU, memory, disk, network, battery, and temperature stats.

        Raises:
            ImportError: If psutil is not installed
            Exception: If stats collection fails
        """
        import psutil  # pylint: disable=import-outside-toplevel

        # CPU statistics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()

        # cpu_freq can fail on FreeBSD with buffer size mismatch
        try:
            cpu_freq = psutil.cpu_freq()
        except (SystemError, RuntimeError) as e:
            logger.debug("cpu_freq not available: %s", e)
            cpu_freq = None

        # Memory statistics
        memory = psutil.virtual_memory()

        # Disk statistics (root filesystem)
        disk = psutil.disk_usage("/")

        # Network statistics
        net_io = psutil.net_io_counters()
        current_time = time.time()

        # Calculate network rates (bytes per second)
        net_recv_rate = 0.0
        net_sent_rate = 0.0
        if SystemStatsService._last_net_io and SystemStatsService._last_net_time:
            time_delta = current_time - SystemStatsService._last_net_time
            if time_delta > 0:
                # Calculate rates in MB/s
                net_recv_rate = (
                    (net_io.bytes_recv - SystemStatsService._last_net_io.bytes_recv)
                    / time_delta
                    / (1024**2)
                )
                net_sent_rate = (
                    (net_io.bytes_sent - SystemStatsService._last_net_io.bytes_sent)
                    / time_delta
                    / (1024**2)
                )

        # Store current readings for next calculation
        SystemStatsService._last_net_io = net_io
        SystemStatsService._last_net_time = current_time

        # Process count
        processes = len(psutil.pids())

        # System uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time

        stats = {
            "cpu_percent": round(cpu_percent, 1),
            "cpu_count": cpu_count,
            "cpu_freq_current": round(cpu_freq.current, 1) if cpu_freq else None,
            "cpu_freq_max": round(cpu_freq.max, 1) if cpu_freq else None,
            "memory_percent": round(memory.percent, 1),
            "memory_used_mb": round(memory.used / (1024**2), 1),
            "memory_total_mb": round(memory.total / (1024**2), 1),
            "memory_available_mb": round(memory.available / (1024**2), 1),
            "disk_percent": round(disk.percent, 1),
            "disk_used_gb": round(disk.used / (1024**3), 1),
            "disk_total_gb": round(disk.total / (1024**3), 1),
            "disk_free_gb": round(disk.free / (1024**3), 1),
            "network_sent_mb": round(net_io.bytes_sent / (1024**2), 1),
            "network_recv_mb": round(net_io.bytes_recv / (1024**2), 1),
            "network_sent_rate_mbs": round(net_sent_rate, 3),
            "network_recv_rate_mbs": round(net_recv_rate, 3),
            "processes": processes,
            "uptime_seconds": int(uptime_seconds),
        }

        # Conditionally add battery if present
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                stats["battery"] = {
                    "percent": battery.percent,
                    "plugged": battery.power_plugged,
                    "time_left": (
                        battery.secsleft
                        if battery.secsleft
                        not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN)
                        else None
                    ),
                }

        # Conditionally add temperatures if available
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                # Get average temperature from all sensors
                all_temps = []
                for _name, entries in temps.items():
                    for entry in entries:
                        if entry.current:
                            all_temps.append(entry.current)
                if all_temps:
                    stats["temperature_avg"] = round(sum(all_temps) / len(all_temps), 1)

        # Add power management info (Linux only)
        if SystemStatsService._is_linux():
            governors = SystemStatsService.get_cpu_governors()
            if governors.get("available"):
                stats["power_management"] = {
                    "governors": governors,
                    "io_schedulers": SystemStatsService.get_io_schedulers(),
                }

        return stats
