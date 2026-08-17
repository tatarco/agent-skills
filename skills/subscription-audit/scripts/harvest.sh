#!/usr/bin/env bash
# Download every PDF attachment matching a Gmail query.
# Usage:  GMAIL_TOKEN=token_dad.json bash harvest.sh "from:<vendor> newer_than:13m" [outdir]
set -uo pipefail

Q="${1:?usage: harvest.sh \"<gmail query>\" [outdir]}"
OUT="${2:-pdfs}"
G="$HOME/.claude/skills/gmail/gmail_cli.py"
mkdir -p "$OUT"

IDS=$(python3 "$G" search "$Q" --max 60 2>/dev/null | grep -oE '^\[[0-9a-f]+\]' | tr -d '[]')
[ -z "$IDS" ] && { echo "no messages for: $Q"; exit 0; }

n=0
for id in $IDS; do
  python3 "$G" download "$id" --out "$OUT" >/dev/null 2>&1 && n=$((n+1))
done
echo "downloaded attachments from $n message(s) into $OUT/"
ls -1 "$OUT" | tail -20
