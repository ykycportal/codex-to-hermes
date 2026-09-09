# Codex to Hermes Converter

Convert Codex CLI skills/plugins into Hermes Agent-compatible skills.

## Quick Start

```bash
# Convert a single skill
python3 convert.py /path/to/SKILL.md --output ~/.hermes/skills

# Convert entire directory
python3 convert.py /path/to/codex-repo --recursive --output ~/.hermes/skills

# With malware scan
python3 convert.py /path/to/repo --scan --recursive
```

Or use the shell wrapper:

```bash
bash codex-to-hermes.sh /path/to/repo --recursive --scan
```

## What It Does

- Converts `SKILL.md` files from Codex CLI format to Hermes Agent format
- Handles plugin manifests (`.codex-plugin/plugin.json`)
- Updates YAML frontmatter (name, description, tags, triggers)
- Preserves the skill body content
- Optional malware scanning before conversion

## What It Does NOT Do

This is a **skill format converter**, not a full migration tool:

- ❌ No MCP configuration handling (not portable between tools)
- ❌ No routing table conversion (tool-specific)
- ❌ No dependency resolution
- ❌ No security audit (use external scanners for that)

For complex repos with MCP configs or custom routing, manual review is recommended.

## Security

Optional malware scanning:

```bash
python3 scan-malware.py /path/to/repo
```

Checks for:
- Reverse shells
- Credential exfiltration
- Persistence mechanisms
- Data theft patterns

**Note:** Scanner is regex-based. Can be bypassed by obfuscation. Always review converted skills from unknown sources.

## Files

| File | Purpose |
|------|---------|
| `convert.py` | Core conversion logic |
| `codex-to-hermes.sh` | Shell wrapper |
| `scan-malware.py` | Malware scanner |
| `README.md` | This file |

## License

MIT
