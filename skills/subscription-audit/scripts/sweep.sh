#!/usr/bin/env bash
# Sweep a mailbox for recurring-payment signals and rank senders by frequency.
# Usage:  GMAIL_TOKEN=token_dad.json bash sweep.sh [months] [outdir]
# Reads nothing, sends nothing, changes nothing.
set -uo pipefail

MONTHS="${1:-13}"
OUT="${2:-.}"
G="$HOME/.claude/skills/gmail/gmail_cli.py"
RAW="$OUT/sweep_raw.txt"

[ -f "$G" ] || { echo "gmail_cli.py not found at $G — install the gmail skill first" >&2; exit 1; }
if [ -z "${GMAIL_TOKEN:-}" ]; then
  echo "WARNING: GMAIL_TOKEN unset — this will sweep the DEFAULT mailbox." >&2
  echo "         Set GMAIL_TOKEN=token_<name>.json to target another account." >&2
fi

mkdir -p "$OUT"; : > "$RAW"

QUERIES=(
  "newer_than:${MONTHS}m (subject:receipt OR subject:invoice OR subject:renewal OR subject:renew)"
  "newer_than:${MONTHS}m (subject:(subscription OR renewed OR \"auto-renew\" OR membership))"
  "newer_than:${MONTHS}m (from:2checkout OR from:cleverbridge OR from:paddle OR from:nexway OR from:digitalriver OR from:fastspring OR from:avangate)"
  "newer_than:${MONTHS}m (from:googleplay-noreply@google.com OR from:payments-noreply@google.com)"
  "newer_than:${MONTHS}m (from:apple.com subject:(receipt OR invoice OR subscription))"
  "newer_than:${MONTHS}m from:paypal"
  "newer_than:${MONTHS}m has:attachment filename:pdf (subject:(invoice OR statement OR receipt))"
  # Hebrew — replace with the target's language if different
  "newer_than:${MONTHS}m (subject:(חשבונית OR קבלה OR חיוב OR מנוי OR \"הוראת קבע\"))"
)

for q in "${QUERIES[@]}"; do
  echo "##### $q" >> "$RAW"
  python3 "$G" search "$q" --max 60 >> "$RAW" 2>&1
done

echo
echo "=== RECURRING PAYEE CANDIDATES (by frequency) ==="
grep "From:" "$RAW" | sed 's/.*From: //' | sort | uniq -c | sort -rn | head -40
echo
echo "Raw results: $RAW"
echo "Next: harvest.sh \"from:<sender> newer_than:${MONTHS}m\" to pull their invoice PDFs."
