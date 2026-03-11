#!/bin/bash
set -e

SKILL_NAME="visualize-doc-v2"
DEST="$HOME/.claude/skills/$SKILL_NAME"
SRC="$(cd "$(dirname "$0")" && pwd)/skill"

if [ ! -d "$SRC" ]; then
  echo "エラー: skill/ ディレクトリが見つかりません。"
  echo "リポジトリのルートから実行してください。"
  exit 1
fi

# ~/.claude/skills/ がなければ作成
mkdir -p "$HOME/.claude/skills"

# 既存があればバックアップ
if [ -d "$DEST" ]; then
  BACKUP="${DEST}.backup.$(date +%Y%m%d-%H%M%S)"
  echo "既存スキルを検出: バックアップ → $BACKUP"
  mv "$DEST" "$BACKUP"
fi

# コピー
cp -r "$SRC" "$DEST"

echo ""
echo "=== インストール完了 ==="
echo "スキル: $SKILL_NAME"
echo "場所:   $DEST"
echo ""
echo "Claude Code で「図解して」と話しかけてみてください。"
