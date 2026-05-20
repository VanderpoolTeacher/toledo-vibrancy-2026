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
