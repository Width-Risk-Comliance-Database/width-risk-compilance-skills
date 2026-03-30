#!/bin/bash
# Install Width Risk & Compliance skill for Claude Code
# Usage: ./install.sh

set -e

SKILL_NAME="width-risk-compliance"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing Width Risk & Compliance skill..."

# Create skills directory
mkdir -p "$HOME/.claude/skills"

# Symlink or copy
if [ -d "$SKILL_DIR" ]; then
    echo "  Removing existing installation..."
    rm -rf "$SKILL_DIR"
fi

# Create skill directory with proper structure
mkdir -p "$SKILL_DIR/scripts"
mkdir -p "$SKILL_DIR/references"

# Copy SKILL.md (the one Claude reads)
cp "$REPO_DIR/.claude-skill/SKILL.md" "$SKILL_DIR/SKILL.md"

# Copy scripts
cp "$REPO_DIR/scripts/config.py" "$SKILL_DIR/scripts/"
cp "$REPO_DIR/scripts/register.py" "$SKILL_DIR/scripts/"
cp "$REPO_DIR/scripts/screen.py" "$SKILL_DIR/scripts/"
cp "$REPO_DIR/VERSION" "$SKILL_DIR/"

# Install Python dependency
pip install requests -q 2>/dev/null || pip3 install requests -q 2>/dev/null || true

echo ""
echo "✅ Installed to: $SKILL_DIR"
echo ""
echo "Usage in Claude Code:"
echo "  \"Use the width-risk-compliance skill to screen 赵长鹏\""
echo ""
echo "Or directly:"
echo "  python3 $SKILL_DIR/scripts/register.py"
echo "  python3 $SKILL_DIR/scripts/screen.py --name '赵长鹏' --country CN"
