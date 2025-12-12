"""System statistics service."""

import logging
import time

logger = logging.getLogger(__name__)


class SystemStatsService:
    """Service for collecting system statistics."""

    # Class variable to store last network I/O reading for rate calculation
    _last_net_io = None
    _last_net_time = None

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

        return stats
