#!/usr/bin/env python3
"""
convert.py — Core conversion logic for Codex CLI → Hermes Agent skills

Handles:
- SKILL.md files in .agents/skills/<name>/ or skills/<name>/
- Plugin manifests (.codex-plugin/plugin.json)
- Conversion strips Codex-specific syntax, adds Hermes triggers

Usage:
    python3 convert.py <input-path> [--output <dir>] [--recursive]
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


def parse_frontmatter(content: str) -> tuple[Dict, str]:
    """Extract frontmatter YAML and body from skill file."""
    if not content.startswith('---'):
        return {}, content
    
    # Find closing ---
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if not match:
        return {}, content
    
    yaml_content = match.group(1)
    body = match.group(2)
    
    # Parse simple YAML (no full parser needed for our use case)
    frontmatter = {}
    for line in yaml_content.split('\n'):
        line = line.strip()
        if ':' in line and not line.startswith('#'):
            key, _, value = line.partition(':')
            value = value.strip().strip('"').strip("'")
            
            # Handle arrays like [tag1, tag2]
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',')]
            
            frontmatter[key.strip()] = value
    
    return frontmatter, body


def convert_codex_plugin(plugin_json: Path) -> Optional[Dict]:
    """Convert Codex plugin manifest to Hermes skill format."""
    try:
        with open(plugin_json, 'r') as f:
            data = json.load(f)
        
        # Extract relevant fields
        skill = {
            'name': data.get('name', plugin_json.parent.name),
            'description': data.get('description', ''),
            'version': data.get('version', '1.0.0'),
            'author': data.get('author', 'unknown'),
        }
        
        # Convert commands to triggers
        commands = data.get('commands', [])
        if commands:
            skill['triggers'] = commands
        
        # Convert tools to MCP tools
        tools = data.get('tools', [])
        if tools:
            skill['tools'] = tools
        
        return skill
    except Exception as e:
        print(f"  ⚠️  Failed to parse {plugin_json}: {e}")
        return None


def convert_to_hermes(frontmatter: Dict, body: str) -> str:
    """Convert Codex/Claude frontmatter to Hermes format."""
    
    # Extract fields
    name = frontmatter.get('name', 'unknown-skill')
    description = frontmatter.get('description', '')
    category = frontmatter.get('category', 'general')
    tags = frontmatter.get('tags', [])
    triggers = frontmatter.get('triggers', [])
    
    # Ensure name is snake_case
    name = re.sub(r'[^a-z0-9-]', '-', name.lower())
    name = re.sub(r'-+', '-', name).strip('-')
    
    # Build triggers list
    skill_triggers = [name]
    if triggers:
        skill_triggers.extend(triggers)
    
    # Build tags list
    skill_tags = list(tags) if isinstance(tags, list) else [tags] if tags else []
    if category and category not in skill_tags:
        skill_tags.append(category)
    
    # Convert description to Hermes format
    desc = description.replace('\n', ' ').strip()
    
    # Write Hermes SKILL.md
    output = f"""---
name: {name}
description: "{desc}"
category: {category}
tags: [{', '.join(skill_tags)}]
triggers:
"""
    for trigger in skill_triggers:
        output += f"  - \"{trigger}\"\n"
    
    output += """---
"""
    
    # Append body (skip original frontmatter if present)
    if body:
        output += body
    
    return output


def convert_file(input_path: Path, output_dir: Path, recursive: bool = False) -> tuple[int, int]:
    """Convert a single SKILL.md file. Returns (converted, skipped) counts."""
    
    if not input_path.name == 'SKILL.md':
        return 0, 0
    
    try:
        content = input_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  ⚠️  Could not read {input_path}: {e}")
        return 0, 1
    
    frontmatter, body = parse_frontmatter(content)
    
    if not frontmatter:
        # No frontmatter, might not be a valid skill
        return 0, 1
    
    # Determine output path
    skill_name = frontmatter.get('name', input_path.stem)
    skill_name = re.sub(r'[^a-z0-9-]', '-', skill_name.lower())
    skill_name = re.sub(r'-+', '-', skill_name).strip('-')
    
    # For recursive mode, preserve directory structure
    if recursive:
        try:
            rel_path = input_path.relative_to(input_path.parent.parent)
            output_path = output_dir / rel_path.parent / f"{skill_name}.md"
        except ValueError:
            output_path = output_dir / f"{skill_name}.md"
    else:
        output_path = output_dir / f"{skill_name}.md"
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert and write
    try:
        converted = convert_to_hermes(frontmatter, body)
        output_path.write_text(converted, encoding='utf-8')
        print(f"  ✓ {skill_name}")
        return 1, 0
    except Exception as e:
        print(f"  ✗ Failed to convert {input_path.name}: {e}")
        return 0, 1


def convert_plugin(plugin_path: Path, output_dir: Path) -> tuple[int, int]:
    """Convert a Codex plugin manifest to Hermes skill."""
    
    try:
        skill_data = convert_codex_plugin(plugin_path)
        if not skill_data:
            return 0, 1
        
        skill_name = skill_data.get('name', plugin_path.parent.name)
        skill_name = re.sub(r'[^a-z0-9-]', '-', skill_name.lower())
        skill_name = re.sub(r'-+', '-', skill_name).strip('-')
        
        output_path = output_dir / f"{skill_name}-plugin.md"
        
        # Write Hermes format
        output = f"""---
name: {skill_name}-plugin
description: "{skill_data.get('description', '')}"
category: plugin
tags: [codex, plugin, {skill_name}]
triggers:
  - "{skill_name}-plugin"
  - "{skill_name}"
---

# {skill_name} Plugin (Codex → Hermes)

**Original:** {plugin_path.parent.name}  
**Version:** {skill_data.get('version', 'unknown')}  
**Author:** {skill_data.get('author', 'unknown')}

## Commands
"""
        for cmd in skill_data.get('triggers', []):
            output += f"- `{cmd}`\n"
        
        output += """
## Notes
This was auto-converted from a Codex plugin manifest.
Manual review recommended for full functionality.
"""
        
        output_path.write_text(output, encoding='utf-8')
        print(f"  ✓ {skill_name}-plugin")
        return 1, 0
    except Exception as e:
        print(f"  ✗ Failed to convert plugin {plugin_path}: {e}")
        return 0, 1


def convert_directory(input_path: Path, output_dir: Path, recursive: bool = False) -> tuple[int, int]:
    """Convert all SKILL.md and plugin files in a directory."""
    
    converted = 0
    skipped = 0
    
    # Find all SKILL.md files
    if recursive:
        skill_files = list(input_path.rglob('SKILL.md'))
    else:
        skill_files = list(input_path.glob('*/SKILL.md')) + list(input_path.glob('SKILL.md'))
    
    # Find plugin manifests
    plugin_files = list(input_path.rglob('.codex-plugin/plugin.json'))
    if not recursive:
        plugin_files = list(input_path.glob('.codex-plugin/plugin.json'))
    
    total = len(skill_files) + len(plugin_files)
    print(f"\n📁 Found {total} item(s) to convert:")
    print(f"   • {len(skill_files)} SKILL.md file(s)")
    print(f"   • {len(plugin_files)} plugin manifest(s)\n")
    
    for skill_file in skill_files:
        c, s = convert_file(skill_file, output_dir, recursive)
        converted += c
        skipped += s
    
    for plugin_file in plugin_files:
        c, s = convert_plugin(plugin_file, output_dir)
        converted += c
        skipped += s
    
    return converted, skipped


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert Codex CLI skills to Hermes format')
    parser.add_argument('input', help='Path to input directory or SKILL.md file')
    parser.add_argument('--output', default='~/.hermes/skills', help='Output directory')
    parser.add_argument('--recursive', action='store_true', help='Recursively convert all skills')
    
    args = parser.parse_args()
    
    input_path = Path(args.input).expanduser()
    output_dir = Path(args.output).expanduser()
    
    if not input_path.exists():
        print(f"❌ Input path does not exist: {input_path}")
        sys.exit(1)
    
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"═══════════════════════════════════════════════════════════")
    print(f"  CODEX TO HERMES CONVERTER")
    print(f"═══════════════════════════════════════════════════════════")
    print(f"")
    print(f"  Input:    {input_path}")
    print(f"  Output:   {output_dir}")
    print(f"  Recursive: {args.recursive}")
    print(f"")
    print(f"═══════════════════════════════════════════════════════════")
    
    if input_path.is_file():
        if input_path.name == 'plugin.json' and '.codex-plugin' in str(input_path):
            converted, skipped = convert_plugin(input_path, output_dir)
        else:
            converted, skipped = convert_file(input_path, output_dir, args.recursive)
    else:
        converted, skipped = convert_directory(input_path, output_dir, args.recursive)
    
    print(f"\n{'='*50}")
    print(f"  Conversion Complete!")
    print(f"  ✓ Converted: {converted}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"{'='*50}\n")
    
    if converted == 0:
        print("⚠️  No skills were converted. Check input path.")
        sys.exit(1)


if __name__ == '__main__':
    main()
