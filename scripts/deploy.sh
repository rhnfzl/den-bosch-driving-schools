#!/usr/bin/env bash
# Regenerate + publish the Den Bosch driving-school tool to GitHub.
# GitHub Pages auto-rebuilds, so the live URL updates ~1 min after this runs.
#
# Usage:
#   scripts/deploy.sh           # regenerate the HTML, sync data, push
#   scripts/deploy.sh --full    # re-run enrich -> report -> html first
#                               # (does NOT re-run the Tavily/OpenAI research gathering)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_URL="https://github.com/rhnfzl/den-bosch-driving-schools.git"
WORK="${DEPLOY_DIR:-$HOME/.cache/dbds-deploy}"
ARTIFACT="$ROOT/docs/human-html/2026-06-08-decision-den-bosch-rijschool-explorer.html"
LIVE="https://rhnfzl.github.io/den-bosch-driving-schools/"

cd "$ROOT"
if [ "${1:-}" = "--full" ]; then
  echo "==> Full regen: enrich -> report -> html"
  python3 scripts/enrich.py >/dev/null
  python3 scripts/make_report.py >/dev/null
fi
python3 scripts/make_html.py >/dev/null
echo "==> Built artifact"

# Fresh, clean publish checkout (persistent cache dir).
if [ -d "$WORK/.git" ]; then
  git -C "$WORK" fetch -q origin && git -C "$WORK" reset -q --hard origin/main
else
  mkdir -p "$(dirname "$WORK")"; rm -rf "$WORK"; git clone -q "$REPO_URL" "$WORK"
fi

cp "$ARTIFACT" "$WORK/index.html"
rsync -a --delete --exclude='__pycache__' --exclude='.DS_Store' --exclude='*.pyc' --exclude='*.env' \
  scripts data report research "$WORK/"

git -C "$WORK" add -A
if git -C "$WORK" diff --cached --quiet; then
  echo "==> Nothing changed — already up to date."
  exit 0
fi
git -C "$WORK" -c user.name="rhnfzl" -c user.email="rhnfzl@users.noreply.github.com" \
  commit -q -m "Update tool + data ($(date -u +%F))"
git -C "$WORK" push -q origin main
echo "==> Deployed. Live in ~1 min: $LIVE"
