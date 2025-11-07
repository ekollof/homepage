"""Command-line interface tools for Homepage."""

import argparse
import json
import sys
from pathlib import Path

import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .config import get_config
from .utils import load_toml_file, validate_links_config


def validate_config_command(args):
    """Validate the links configuration file."""
    config = get_config()
    config_file = Path(args.config) if args.config else config.CONFIG_FILE

    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return 1

    print(f"📋 Validating configuration: {config_file}")

    # Load TOML
    data = load_toml_file(config_file)
    if data is None:
        print("❌ Failed to parse TOML file")
        return 1

    # Validate structure
    valid, errors = validate_links_config(data)

    if valid:
        print("✅ Configuration structure is valid")
    else:
        print(f"❌ Configuration has {len(errors)} error(s):")
        for error in errors:
            print(f"   - {error}")
        return 1

    # Count items
    categories = data.get("category", [])
    total_links = 0
    for category in categories:
        total_links += len(category.get("links", []))
        for subcat in category.get("subcategory", []):
            total_links += len(subcat.get("links", []))

    print("📊 Statistics:")
    print(f"   - Categories: {len(categories)}")
    print(f"   - Total links: {total_links}")

    # Validate URLs if requested
    if args.check_urls:
        print("\n🔗 Checking URL accessibility...")
        check_urls(data)

    return 0


def check_urls(config_data):
    """Check if URLs are accessible."""
    categories = config_data.get("category", [])
    checked = 0
    failed = []

    for category in categories:
        for link in category.get("links", []):
            url = link.get("url")
            name = link.get("name", "Unknown")
            if check_url(url):
                checked += 1
            else:
                failed.append((name, url))

        for subcat in category.get("subcategory", []):
            for link in subcat.get("links", []):
                url = link.get("url")
                name = link.get("name", "Unknown")
                if check_url(url):
                    checked += 1
                else:
                    failed.append((name, url))

    print(f"   ✅ Accessible: {checked}")
    if failed:
        print(f"   ❌ Failed: {len(failed)}")
        for name, url in failed[:10]:  # Show first 10
            print(f"      - {name}: {url}")
        if len(failed) > 10:
            print(f"      ... and {len(failed) - 10} more")


def check_url(url: str, timeout: int = 5) -> bool:
    """Check if a URL is accessible."""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 400
    except requests.RequestException:
        return False


def stats_command(args):
    """Show application statistics."""
    config = get_config()
    url = f"http://{config.HOST}:{config.PORT}/api/stats"

    print(f"📊 Fetching statistics from {url}...")

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("\n✅ Application Statistics:")
            print(f"   Uptime: {stats.get('uptime_formatted', 'N/A')}")
            print(f"   Requests: {stats.get('request_count', 0)}")
            print(f"   Page views: {stats.get('page_views', 0)}")
            print(f"   Searches: {stats.get('search_count', 0)}")
            print(f"   Link clicks: {stats.get('link_clicks_total', 0)}")

            top_links = stats.get("top_links", [])
            if top_links:
                print("\n🔗 Top Links:")
                for i, (name, count) in enumerate(top_links[:5], 1):
                    print(f"   {i}. {name}: {count} clicks")

            providers = stats.get("search_providers", {})
            if providers:
                print("\n🔍 Search Providers:")
                for provider, count in providers.items():
                    print(f"   - {provider}: {count} searches")

            if args.export:
                export_file = Path(args.export)
                with open(export_file, "w", encoding="utf-8") as f:
                    json.dump(stats, f, indent=2)
                print(f"\n💾 Statistics exported to: {export_file}")

            return 0

        print(f"❌ Error: HTTP {response.status_code}")
        return 1
    except requests.RequestException as e:
        print(f"❌ Failed to connect: {e}")
        print("   Make sure the application is running.")
        return 1


def health_command(args):  # pylint: disable=unused-argument
    """Check application health."""
    config = get_config()
    url = f"http://{config.HOST}:{config.PORT}/health"

    print(f"🏥 Checking health at {url}...")

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Status: {health.get('status', 'unknown')}")
            print(f"   Version: {health.get('version', 'unknown')}")
            print(f"   Uptime: {health.get('uptime', 0):.2f}s")
            return 0

        print(f"❌ Unhealthy: HTTP {response.status_code}")
        return 1
    except requests.RequestException as e:
        print(f"❌ Cannot reach application: {e}")
        return 1


def export_config_command(args):
    """Export configuration to different format."""
    config = get_config()
    config_file = Path(args.config) if args.config else config.CONFIG_FILE
    output_file = Path(args.output)

    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return 1

    print(f"📤 Exporting {config_file} to {output_file}...")

    data = load_toml_file(config_file)
    if data is None:
        print("❌ Failed to load configuration")
        return 1

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            if output_file.suffix == ".json":
                json.dump(data, f, indent=2)
            else:
                print(f"❌ Unsupported output format: {output_file.suffix}")
                return 1

        print(f"✅ Exported successfully to {output_file}")
        return 0
    except OSError as e:
        print(f"❌ Failed to write file: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Homepage CLI - Manage and monitor your homepage")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate links configuration")
    validate_parser.add_argument(
        "-c", "--config", help="Path to configuration file (default: links.toml)"
    )
    validate_parser.add_argument(
        "--check-urls", action="store_true", help="Check URL accessibility"
    )
    validate_parser.set_defaults(func=validate_config_command)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show application statistics")
    stats_parser.add_argument("-e", "--export", help="Export statistics to JSON file")
    stats_parser.set_defaults(func=stats_command)

    # Health command
    health_parser = subparsers.add_parser("health", help="Check application health")
    health_parser.set_defaults(func=health_command)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export configuration to different format")
    export_parser.add_argument(
        "-c", "--config", help="Path to configuration file (default: links.toml)"
    )
    export_parser.add_argument("-o", "--output", required=True, help="Output file path")
    export_parser.set_defaults(func=export_config_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
