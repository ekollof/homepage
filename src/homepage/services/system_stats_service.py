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
    def _is_freebsd() -> bool:
        """Check if running on FreeBSD."""
        return platform.system() == "FreeBSD"

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
    def get_freebsd_power_management() -> dict:
        """Get FreeBSD power management information.

        Returns:
            Dictionary with powerd status, CPU frequency levels, and current settings.
        """
        if not SystemStatsService._is_freebsd():
            return {"available": False, "reason": "Not FreeBSD"}

        try:
            import subprocess  # pylint: disable=import-outside-toplevel

            power_info: dict = {
                "available": True,
                "cpu_freq": {},
                "powerd": {},
            }

            # Get CPU frequency information via sysctl
            try:
                # Get available frequency levels
                result = subprocess.run(
                    ["sysctl", "-n", "dev.cpu.0.freq_levels"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    # Parse format: "2400/-1 2200/-1 2000/-1 1800/-1 ..."
                    freq_levels = []
                    for level in result.stdout.strip().split():
                        freq = level.split("/")[0]
                        freq_levels.append(int(freq))

                    power_info["cpu_freq"]["available_levels"] = sorted(freq_levels, reverse=True)

                # Get current frequency
                result = subprocess.run(
                    ["sysctl", "-n", "dev.cpu.0.freq"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    power_info["cpu_freq"]["current"] = int(result.stdout.strip())

            except (ValueError, IndexError, subprocess.TimeoutExpired) as e:
                logger.debug("Failed to get CPU frequency info: %s", e)

            # Check powerd status
            try:
                # Check if powerd is enabled in rc.conf
                result = subprocess.run(
                    ["sysrc", "-n", "powerd_enable"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                powerd_enabled = result.returncode == 0 and result.stdout.strip().upper() == "YES"
                power_info["powerd"]["enabled"] = powerd_enabled

                # Check if powerd is actually running
                result = subprocess.run(
                    ["pgrep", "-q", "powerd"],
                    capture_output=True,
                    timeout=5,
                    check=False,
                )
                powerd_running = result.returncode == 0
                power_info["powerd"]["running"] = powerd_running

                # Get powerd flags if enabled
                if powerd_enabled:
                    result = subprocess.run(
                        ["sysrc", "-n", "powerd_flags"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False,
                    )
                    if result.returncode == 0:
                        flags = result.stdout.strip()
                        power_info["powerd"]["flags"] = flags

                        # Parse mode from flags (-a for AC, -b for battery)
                        # Default modes if not specified
                        ac_mode = "hiadaptive"
                        battery_mode = "adaptive"

                        if "-a" in flags:
                            parts = flags.split()
                            try:
                                ac_idx = parts.index("-a")
                                if ac_idx + 1 < len(parts):
                                    ac_mode = parts[ac_idx + 1]
                            except (ValueError, IndexError):
                                pass

                        if "-b" in flags:
                            parts = flags.split()
                            try:
                                bat_idx = parts.index("-b")
                                if bat_idx + 1 < len(parts):
                                    battery_mode = parts[bat_idx + 1]
                            except (ValueError, IndexError):
                                pass

                        power_info["powerd"]["ac_mode"] = ac_mode
                        power_info["powerd"]["battery_mode"] = battery_mode

                # Get available powerd modes
                power_info["powerd"]["available_modes"] = [
                    "minimum",
                    "adaptive",
                    "hiadaptive",
                    "maximum",
                ]

            except subprocess.TimeoutExpired as e:
                logger.debug("Timeout checking powerd: %s", e)

            # Get ACPI battery status if available
            try:
                result = subprocess.run(
                    ["sysctl", "-n", "hw.acpi.battery.life"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    power_info["battery_life"] = int(result.stdout.strip())

                result = subprocess.run(
                    ["sysctl", "-n", "hw.acpi.acline"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    power_info["ac_connected"] = result.stdout.strip() == "1"

            except (ValueError, subprocess.TimeoutExpired) as e:
                logger.debug("Failed to get battery info: %s", e)

            return power_info

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to get FreeBSD power management info: %s", e)
            return {"available": False, "reason": str(e)}

    @staticmethod
    def set_freebsd_cpu_freq(freq: int) -> dict:
        """Set CPU frequency on FreeBSD.

        Args:
            freq: Target frequency in MHz

        Returns:
            Dictionary with success status and message
        """
        if not SystemStatsService._is_freebsd():
            return {"success": False, "message": "Not FreeBSD"}

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
            cmd = [escalator, str(helper_script), "set-freebsd-freq", str(freq)]

            # Add non-interactive flag for sudo
            if escalator == "sudo":
                cmd = ["sudo", "-n", str(helper_script), "set-freebsd-freq", str(freq)]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                env={"PATH": "/usr/bin:/bin:/usr/local/bin:/sbin:/usr/sbin"},
            )

            if result.returncode == 0:
                return {"success": True, "message": result.stdout.strip()}
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return {"success": False, "message": error_msg or "Failed to set frequency"}

        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Operation timed out (30s limit)"}
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to set CPU frequency: %s", e)
            return {"success": False, "message": str(e)}

    @staticmethod
    def _is_zfs_available() -> bool:
        """Check if ZFS is available on the system."""
        try:
            # Check if ZFS kernel module is loaded via sysctl
            if SystemStatsService._is_freebsd():
                result = SystemStatsService._read_sysctl("kstat.zfs.misc.arcstats.size")
                return result is not None
            elif SystemStatsService._is_linux():
                # On Linux, check if /proc/spl/kstat/zfs/arcstats exists
                return Path("/proc/spl/kstat/zfs/arcstats").exists()
            return False
        except Exception as e:  # pylint: disable=broad-except
            logger.debug("ZFS availability check failed: %s", e)
            return False

    @staticmethod
    def _read_sysctl(name: str) -> str | None:
        """Read a sysctl value (cross-platform).

        Args:
            name: sysctl variable name

        Returns:
            Value as string or None if not available
        """
        import subprocess  # pylint: disable=import-outside-toplevel

        try:
            result = subprocess.run(
                ["sysctl", "-n", name],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.debug("Failed to read sysctl %s: %s", name, e)
            return None

    @staticmethod
    def get_zfs_stats() -> dict:
        """Get ZFS ARC statistics and pool information.

        Returns:
            Dictionary with ZFS stats or {"available": False}
        """
        if not SystemStatsService._is_zfs_available():
            return {"available": False, "reason": "ZFS not loaded"}

        try:
            import subprocess  # pylint: disable=import-outside-toplevel

            stats: dict = {"available": True}

            # Get ARC statistics
            arc_stats = {}
            
            if SystemStatsService._is_freebsd():
                # FreeBSD: use sysctl
                size = SystemStatsService._read_sysctl("kstat.zfs.misc.arcstats.size")
                c_max = SystemStatsService._read_sysctl("kstat.zfs.misc.arcstats.c_max")
                hits = SystemStatsService._read_sysctl("kstat.zfs.misc.arcstats.hits")
                misses = SystemStatsService._read_sysctl("kstat.zfs.misc.arcstats.misses")

                if size and c_max and hits and misses:
                    arc_stats = {
                        "size_bytes": int(size),
                        "max_bytes": int(c_max),
                        "hits": int(hits),
                        "misses": int(misses),
                    }
            elif SystemStatsService._is_linux():
                # Linux: read from /proc/spl/kstat/zfs/arcstats
                arcstats_file = Path("/proc/spl/kstat/zfs/arcstats")
                if arcstats_file.exists():
                    content = arcstats_file.read_text()
                    # Parse the file - format is "name type value"
                    for line in content.splitlines():
                        parts = line.split()
                        if len(parts) >= 3:
                            name, value = parts[0], parts[2]
                            if name == "size":
                                arc_stats["size_bytes"] = int(value)
                            elif name == "c_max":
                                arc_stats["max_bytes"] = int(value)
                            elif name == "hits":
                                arc_stats["hits"] = int(value)
                            elif name == "misses":
                                arc_stats["misses"] = int(value)

            if arc_stats:
                # Calculate derived metrics
                total_requests = arc_stats["hits"] + arc_stats["misses"]
                if total_requests > 0:
                    hit_ratio = (arc_stats["hits"] / total_requests) * 100
                else:
                    hit_ratio = 0.0

                stats["arc"] = {
                    "size_mb": round(arc_stats["size_bytes"] / (1024**2), 1),
                    "max_mb": round(arc_stats["max_bytes"] / (1024**2), 1),
                    "size_percent": round(
                        (arc_stats["size_bytes"] / arc_stats["max_bytes"]) * 100, 1
                    ),
                    "hit_ratio": round(hit_ratio, 1),
                    "hits": arc_stats["hits"],
                    "misses": arc_stats["misses"],
                }

            # Get pool information using zpool list
            try:
                result = subprocess.run(
                    ["zpool", "list", "-H", "-o", "name,health,size,alloc,free"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )

                if result.returncode == 0 and result.stdout.strip():
                    pools = []
                    for line in result.stdout.strip().splitlines():
                        parts = line.split()
                        if len(parts) >= 5:
                            pools.append(
                                {
                                    "name": parts[0],
                                    "health": parts[1],
                                    "size": parts[2],
                                    "allocated": parts[3],
                                    "free": parts[4],
                                }
                            )
                    if pools:
                        stats["pools"] = pools
            except Exception as e:  # pylint: disable=broad-except
                logger.debug("Failed to get zpool info: %s", e)

            return stats

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to get ZFS stats: %s", e)
            return {"available": False, "reason": str(e)}

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

        # Add power management info (FreeBSD only)
        if SystemStatsService._is_freebsd():
            freebsd_power = SystemStatsService.get_freebsd_power_management()
            if freebsd_power.get("available"):
                stats["power_management"] = {
                    "freebsd": freebsd_power,
                }

        # Add ZFS stats if available (FreeBSD or Linux with ZFS)
        zfs_stats = SystemStatsService.get_zfs_stats()
        if zfs_stats.get("available"):
            stats["zfs"] = zfs_stats

        return stats
