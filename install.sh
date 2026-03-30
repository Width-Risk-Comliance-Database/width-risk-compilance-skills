#!/bin/bash
# Install Width Risk & Compliance skill for Claude Code
set -e

SKILL_NAME="width-risk-compliance"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing Width Risk & Compliance skill..."

mkdir -p "$SKILL_DIR"
rm -rf "$SKILL_DIR"/*

cp "$REPO_DIR/.claude-skill/SKILL.md" "$SKILL_DIR/SKILL.md"
cp "$REPO_DIR/VERSION" "$SKILL_DIR/" 2>/dev/null || true

echo ""
echo "✅ Installed to: $SKILL_DIR"
echo ""
echo "Usage: tell your Agent —"
echo "  \"帮我查一下赵长鹏\""
echo "  \"screen Thaksin Shinawatra\""
