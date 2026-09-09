#!/bin/bash
# codex-to-hermes.sh — Convert Codex CLI skills to Hermes Agent skills
# Usage: bash codex-to-hermes.sh <path> [--scan] [--recursive] [--output <dir>]

set -e

INPUT="${1:?Usage: bash codex-to-hermes.sh <path> [--scan] [--recursive] [--output <dir>]}"
SCAN=false
RECURSIVE=false
OUTPUT="$HOME/.hermes/skills"

while [[ $# -gt 0 ]]; do
    case $1 in
        --scan) SCAN=true ;;
        --recursive) RECURSIVE=true ;;
        --output) OUTPUT="$2"; shift ;;
        *) break ;;
    esac
    shift
done

echo "═══════════════════════════════════════════════"
echo "  CODEX TO HERMES SKILL CONVERTER"
echo "═══════════════════════════════════════════════"
echo ""
echo "  Input:    $INPUT"
echo "  Output:   $OUTPUT"
echo "  Recursive: $RECURSIVE"
echo "  Scan:     $SCAN"
echo ""
echo "═══════════════════════════════════════════════"
echo ""

# Resolve input path
if [[ ! -d "$INPUT" ]]; then
    echo "[!] Input path does not exist: $INPUT"
    exit 1
fi

# Run scan if requested
if [ "$SCAN" = true ]; then
    echo "[*] Running malware & backdoor scan..."
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python3 "$SCRIPT_DIR/scan-malware.py" "$INPUT"
    echo ""
fi

# Find SKILL.md files recursively
if [ "$RECURSIVE" = true ]; then
    mapfile -t FILES < <(find "$INPUT" -name "SKILL.md" -type f 2>/dev/null | sort)
else
    FILES=()
    if [ -f "$INPUT/SKILL.md" ]; then
        FILES=("$INPUT/SKILL.md")
    else
        for dir in "$INPUT"/*/; do
            if [ -f "$dir/SKILL.md" ]; then
                FILES+=("$dir/SKILL.md")
            fi
        done
    fi
fi

if [ ${#FILES[@]} -eq 0 ]; then
    echo "[!] No SKILL.md files found in $INPUT"
    exit 0
fi

COUNT=${#FILES[@]}
echo "[*] Found $COUNT SKILL.md file(s)"
echo "[*] Output directory: $OUTPUT"
echo ""

# Convert each skill
SUCCESS=0
FAIL=0

for FILE in "${FILES[@]}"; do
    [ -z "$FILE" ] && continue
    SKILL_NAME=$(basename "$(dirname "$FILE")")
    OUTPUT_DIR="$OUTPUT/$SKILL_NAME"

    if [ -d "$OUTPUT_DIR" ] && [ -f "$OUTPUT_DIR/SKILL.md" ]; then
        echo "Skipping (exists): $SKILL_NAME"
        continue
    fi

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    # Read original frontmatter
    NAME=$(sed -n 's/^name: *//p' "$FILE" | head -1 | sed 's/^"//;s/"$//')
    DESCRIPTION=$(sed -n 's/^description: *//p' "$FILE" | head -1 | sed 's/^"//;s/"$//')

    # Generate triggers
    TRIGGERS="  - \"$NAME\""

    # Determine category based on name
    CATEGORY="general"
    case "$NAME" in
        *research*|*search*|*market*) CATEGORY="research" ;;
        *code*|*test*|*build*|*debug*) CATEGORY="development" ;;
        *design*|*write*|*create*) CATEGORY="creative" ;;
        *api*|*web*|*http*) CATEGORY="integration" ;;
        *security*|*audit*|*review*) CATEGORY="security" ;;
        *email*|*comm*|*social*) CATEGORY="communication" ;;
        *data*|*analyzer*|*report*) CATEGORY="analytics" ;;
    esac

    # Read original content (everything after frontmatter)
    CONTENT=$(sed -n '/^---$/,/^---$/!p' "$FILE" | sed '1d;$d' | sed '/^$/d')

    # Write new SKILL.md with Hermes frontmatter
    cat > "$OUTPUT_DIR/SKILL.md" << 'HEADER'
---
HEADER

    cat >> "$OUTPUT_DIR/SKILL.md" << EOF
name: $NAME
description: "$DESCRIPTION"
category: $CATEGORY
tags: [$NAME]
triggers:
EOF
    echo "$TRIGGERS" >> "$OUTPUT_DIR/SKILL.md"

    echo "" >> "$OUTPUT_DIR/SKILL.md"
    echo "$CONTENT" >> "$OUTPUT_DIR/SKILL.md"

    echo "Converting: $SKILL_NAME/SKILL.md"
    echo "  ✓ -> $OUTPUT_DIR/SKILL.md"
    SUCCESS=$((SUCCESS + 1))
done

echo ""
echo "============================================================"
echo "Conversion complete: $SUCCESS/$COUNT skills"
echo "Output: $OUTPUT"
echo "============================================================"
