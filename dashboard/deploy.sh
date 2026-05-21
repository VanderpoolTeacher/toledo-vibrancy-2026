#!/usr/bin/env bash
# Toledo Dashboard deploy helper.
# Commits any pending changes in the parent repo (toledo-vibrancy-2026)
# and pushes to origin. The dashboard lives at dashboard/, so we commit
# from the repo root to include both dashboard/ and any other changes.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Error: $REPO_ROOT is not a git repository."
  exit 1
fi

# Validate every JSON file under dashboard/ BEFORE staging. A broken JSON
# would 404-poison the dashboard until the next manual fix. Running this
# pre-stage means an aborted run doesn't leave corrupt files in the index.
if command -v jq >/dev/null 2>&1; then
  bad_files=()
  while IFS= read -r f; do
    if ! jq empty "$f" >/dev/null 2>&1; then
      bad_files+=("$f")
    fi
  done < <(find dashboard -name '*.json' -type f)
  if [ ${#bad_files[@]} -gt 0 ]; then
    echo "Invalid JSON in:"
    printf '  %s\n' "${bad_files[@]}"
    echo "Aborting deploy."
    exit 1
  fi
else
  echo "WARNING: jq not installed; skipping JSON validation."
fi

# Stage dashboard changes only (don't accidentally commit the Vibrancy map)
git add dashboard/

# If nothing to commit, exit cleanly
if git diff --staged --quiet; then
  echo "No changes to deploy."
  exit 0
fi

MSG="${1:-Dashboard daily update: $(date '+%Y-%m-%d %H:%M')}"
git commit -m "$MSG"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
git push origin "$BRANCH"

echo "Deployed to origin/$BRANCH"
