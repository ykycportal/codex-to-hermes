# codex-to-hermes

Convert Codex CLI skills/plugins into Hermes Agent-compatible skills.

## Quick Start

```bash
# Clone and convert
git clone https://github.com/ykycportal/codex-repo.git
python3 convert.py ./codex-repo --recursive --output ~/.hermes/skills

# With malware scan
python3 convert.py ./codex-repo --scan --recursive
```

## What It Does

- Converts SKILL.md files from Codex CLI format to Hermes Agent format
- Handles plugin manifests (.codex-plugin/plugin.json)
- Preserves skill content while updating frontmatter
- Optional security scanning for backdoors/malware

## Files

| File | Purpose |
|------|---------|
| `convert.py` | Core conversion logic (Python) |
| `codex-to-hermes.sh` | Shell wrapper (optional) |
| `scan-malware.py` | Security scanner (report-only) |
| `README.md` | This file |

## Usage

```bash
# Convert single skill
python3 convert.py path/to/SKILL.md --output ~/.hermes/skills

# Convert entire directory
python3 convert.py ./codex-skills --recursive --output ~/.hermes/skills

# With security scan
python3 convert.py ./codex-skills --scan --recursive
```

## Security Note

The malware scanner uses regex patterns to detect suspicious code.
It reports findings but does NOT block conversion — you decide.

For production use, consider:
- Manual review of converted skills
- Additional testing before deployment
- Scanning source repos with SkillSpector first

## License

MIT
