#!/bin/bash
# whorl_audit.sh — read-only. Compares all Whorl copies against RootBase/Whorl
# to find which are identical (safe to delete later) vs actually diverged.
set -uo pipefail

CANONICAL=~/RootBase/Whorl
OUT=~/WHORL_AUDIT_$(date +%Y%m%d_%H%M%S).md

{
  echo "# Whorl duplication audit — $(date)"
  echo "Canonical assumed: $CANONICAL"
  echo ""

  for f in whorl.py whorl_runtime.py whorl_scribe.py whorl_warp.py; do
    echo "## $f"
    canonical_hash=$(find "$CANONICAL" -name "$f" -exec sha256sum {} \; 2>/dev/null | head -1 | awk '{print $1}')
    echo "Canonical hash: ${canonical_hash:-NOT FOUND}"
    echo ""
    find ~ -name "$f" -not -path "*/.*" 2>/dev/null | while read -r path; do
      h=$(sha256sum "$path" 2>/dev/null | awk '{print $1}')
      if [[ "$h" == "$canonical_hash" ]]; then
        echo "  IDENTICAL: $path"
      else
        echo "  DIFFERS:   $path  (needs manual review before delete)"
      fi
    done
    echo ""
  done
} > "$OUT"

echo "Audit written: $OUT"
cat "$OUT"
