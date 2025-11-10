#!/usr/bin/env python3
"""Render Jinja2 template to extract JavaScript for linting."""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Load environment from .env if it exists
env_file = project_root / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from jinja2 import Environment, FileSystemLoader


class MockConfig:
    """Mock config object with all necessary attributes for template rendering."""
    
    # Clock settings
    CLOCK_FORMAT = '24'
    RELOAD_INTERVAL = 2000
    
    # Feature flags - enable all for complete template rendering
    ENABLE_WEATHER = True
    ENABLE_RSS = True
    ENABLE_SYSTEM_STATS = True
    ENABLE_EDITING = True
    ENABLE_METRICS = True
    ENABLE_WEBSOCKET = True
    
    # Intervals
    SYSTEM_STATS_REFRESH_INTERVAL = 2


def main():
    """Render the JavaScript template and output to stdout."""
    config = MockConfig()
    
    # Setup Jinja2
    template_dir = project_root / 'src' / 'homepage' / 'templates'
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    # Render the JavaScript template
    template = env.get_template('scripts.js.j2')
    rendered = template.render(
        config=config,
        clock_format=config.CLOCK_FORMAT,
        reload_interval=config.RELOAD_INTERVAL
    )
    
    print(rendered)


if __name__ == '__main__':
    main()
