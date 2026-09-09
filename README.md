# codex-to-hermes

Convert Codex CLI skills/plugins into Hermes Agent-compatible skills.

## Quick Start

```bash
# Clone and convert
git clone https://github.com/yourusername/codex-repo.git
bash codex-to-hermes.sh ./codex-repo --scan --recursive

# Output lands in ~/.hermes/skills/
```

## What It Does

Codex skills use the same SKILL.md format but are organized differently:
- Skills live in `.agents/skills/<name>/SKILL.md` or `skills/<name>/SKILL.md`
- Plugin manifests use `.codex-plugin/plugin.json`
- Conversion strips Codex-specific syntax, adds Hermes triggers

## Security

Always scan before converting:
```bash
bash codex-to-hermes.sh <repo> --scan
```

Checks for:
- Reverse shells
- Credential exfiltration
- Persistence mechanisms
- Data theft patterns

## Files

- `codex-to-hermes.sh` — Main entry point
- `scan-malware.py` — Malware/backdoor scanner (report-only)
- `README.md` — This file

## License

MIT
