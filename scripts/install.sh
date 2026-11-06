#!/bin/bash
# ⚡ Flowmap — Claude Code Plugin Installer
# Run: bash scripts/install.sh (from plugin root)

set -e

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="$HOME/.claude/skills/flowmap"
CLAUDE_MD="$HOME/.claude/CLAUDE.md"

echo ""
echo "  ⚡ Flowmap Installer"
echo "  ━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Create directories
mkdir -p "$SKILL_DIR/bin" "$SKILL_DIR/references"

# 2. Copy skill files
cp "$PLUGIN_DIR/skills/flowmap/SKILL.md" "$SKILL_DIR/"
cp "$PLUGIN_DIR/skills/flowmap/references/"* "$SKILL_DIR/references/" 2>/dev/null || true
cp "$PLUGIN_DIR/bin/flowmap.py" "$SKILL_DIR/bin/"
cp "$PLUGIN_DIR/bin/template.html" "$SKILL_DIR/bin/"
cp "$PLUGIN_DIR/commands/flowmap.md" "$SKILL_DIR/"
chmod +x "$SKILL_DIR/bin/flowmap.py"
echo "  ✅ Files installed to $SKILL_DIR"

# 3. Add to CLAUDE.md
[ -f "$CLAUDE_MD" ] || touch "$CLAUDE_MD"
if ! grep -q "flowmap" "$CLAUDE_MD" 2>/dev/null; then
    printf '\n# flowmap\n- **flowmap** (`~/.claude/skills/flowmap/SKILL.md`) - X-ray vision for any project. Maps folder structure, API endpoints, frontend→backend wiring, hook chains, flowcharts. Trigger: `/flowmap`\nWhen the user types `/flowmap`, read `~/.claude/skills/flowmap/SKILL.md` and execute the requested subcommand. For `/flowmap scan`, run `python3 ~/.claude/skills/flowmap/bin/flowmap.py` with zero tokens.\n' >> "$CLAUDE_MD"
    echo "  ✅ Added to ~/.claude/CLAUDE.md"
else
    echo "  ℹ️  Already in CLAUDE.md"
fi

# 4. Shell alias
RC="$HOME/.zshrc"; [ -f "$HOME/.bashrc" ] && RC="$HOME/.bashrc"
if ! grep -q "alias flowmap=" "$RC" 2>/dev/null; then
    printf '\n# Flowmap — project architecture scanner\nalias flowmap="python3 ~/.claude/skills/flowmap/bin/flowmap.py"\n' >> "$RC"
    echo "  ✅ Added 'flowmap' alias to $RC"
else
    echo "  ℹ️  Alias already exists"
fi

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ⚡ Flowmap installed!"
echo ""
echo "  Usage:"
echo "    flowmap .                    # Scan current project (zero tokens)"
echo "    flowmap /path/to/app         # Scan any project"
echo "    /flowmap scan                # Inside Claude Code"
echo "    /flowmap trace \"feature\"     # Trace a feature flow"
echo ""
echo "  Restart shell or: source $RC"
echo ""
