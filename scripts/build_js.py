#!/usr/bin/env python3
"""Build script to combine JavaScript modules into single file."""

import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def main():
    """Combine all JavaScript modules in order."""
    project_root = Path(__file__).parent.parent
    modules_dir = project_root / 'src' / 'homepage' / 'static' / 'js' / 'modules'
    output_file = project_root / 'src' / 'homepage' / 'templates' / 'scripts.js.j2'
    
    if not modules_dir.exists():
        print(f"Error: Modules directory not found: {modules_dir}")
        sys.exit(1)
    
    # Get all .js.j2 files in order (01-xxx.js.j2, 02-xxx.js.j2, etc.)
    module_files = sorted(modules_dir.glob('[0-9][0-9]-*.js.j2'))
    
    if not module_files:
        print(f"Error: No module files found in {modules_dir}")
        sys.exit(1)
    
    print(f"Building JavaScript from {len(module_files)} modules...")
    
    # Combine all modules
    combined_content = []
    combined_content.append("/* ============================================= */")
    combined_content.append("/* Homepage JavaScript - Generated from modules */")
    combined_content.append("/* ============================================= */")
    combined_content.append("")
    
    for module_file in module_files:
        print(f"  • {module_file.name}")
        with open(module_file, 'r') as f:
            content = f.read().strip()
            combined_content.append(f"/* Module: {module_file.stem} */")
            combined_content.append(content)
            combined_content.append("")
    
    # Write combined file
    output_content = '\n'.join(combined_content)
    
    # Add proper indentation for template (8 spaces)
    indented_lines = []
    for line in output_content.split('\n'):
        if line.strip():  # Don't indent empty lines
            indented_lines.append('        ' + line)
        else:
            indented_lines.append('')
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(indented_lines))
    
    print(f"\n✓ Combined {len(module_files)} modules into {output_file}")
    print(f"  Total lines: {len(indented_lines)}")

if __name__ == '__main__':
    main()
