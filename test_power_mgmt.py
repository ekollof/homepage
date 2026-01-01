#!/usr/bin/env python3
"""Quick test script for power management features."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from homepage.services.system_stats_service import SystemStatsService


def main():
    print("Testing power management features...\n")

    # Test platform detection
    print(f"Running on Linux: {SystemStatsService._is_linux()}")
    print()

    # Test CPU governors
    print("=== CPU Governors ===")
    governors = SystemStatsService.get_cpu_governors()
    if governors.get("available"):
        print(f"Power Saving Enabled: {governors.get('power_saving_enabled')}")
        if "current_governor" in governors:
            print(f"Current Governor: {governors['current_governor']}")
            print(f"Available Governors: {', '.join(governors.get('available_governors', []))}")
        else:
            print("Per-CPU governors:")
            for cpu_info in governors.get("cpus", []):
                print(
                    f"  CPU {cpu_info['cpu']}: {cpu_info.get('governor', 'N/A')} "
                    f"({', '.join(cpu_info.get('available_governors', []))})"
                )
    else:
        print(f"Not available: {governors.get('reason')}")
    print()

    # Test I/O schedulers
    print("=== I/O Schedulers ===")
    schedulers = SystemStatsService.get_io_schedulers()
    if schedulers.get("available"):
        for device in schedulers.get("devices", []):
            print(f"{device['device']}: {device['current_scheduler']}")
            print(f"  Available: {', '.join(device['available_schedulers'])}")
    else:
        print(f"Not available: {schedulers.get('reason')}")
    print()

    # Test full stats
    print("=== Full Stats (with power management) ===")
    stats = SystemStatsService.get_stats()
    if "power_management" in stats:
        print("✓ Power management data included in stats")
    else:
        print("✗ Power management data NOT included (expected on non-Linux)")


if __name__ == "__main__":
    main()
