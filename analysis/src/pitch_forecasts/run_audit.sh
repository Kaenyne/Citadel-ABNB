#!/usr/bin/env bash
# Launch one Codex (gpt-6-astra) read-only audit for a batch, detached, and mark completion with a .done file.
# Usage: bash analysis/src/pitch_forecasts/run_audit.sh A01
set -u
BATCH="$1"
ROOT="C:/Users/krish/citadel-abnb"
PF="$ROOT/docs/pitch-forecasts"
PROMPT="$PF/prompts/audit_${BATCH}.md"
OUT="$PF/audits/${BATCH}-research-audit.md"
LOG="$PF/audits/${BATCH}.stdout.log"
DONE="$PF/audits/${BATCH}.done"
mkdir -p "$PF/audits"
rm -f "$DONE"
if [ ! -f "$PROMPT" ]; then echo "missing prompt $PROMPT"; exit 2; fi
(
  cd "$ROOT" && codex exec --ephemeral -s read-only -C "$ROOT" -o "$OUT" "$(cat "$PROMPT")" < /dev/null > "$LOG" 2>&1
  echo "exit=$? $(date)" > "$DONE"
) &
echo "launched audit $BATCH pid $! -> $OUT"
