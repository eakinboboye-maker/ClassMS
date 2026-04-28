#!/usr/bin/env bash
set -euo pipefail

# ClassLite JupyterLite -> Vercel static deploy helper
#
# This version avoids Vercel-side Python builds entirely.
# It builds JupyterLite locally, then uploads the built dist/ folder.
#
# Usage:
#   bash deploy_vercel_static.sh
#
# Optional env vars:
#   JUPYTERLITE_DIR=/absolute/or/relative/path/to/jupyterlite
#   PROD=false                    # preview deploy instead of production
#   SKIP_SYNC=true                # skip scripts/sync_course_content.py
#   SKIP_LOCAL_BUILD=true         # skip jupyter lite build

JUPYTERLITE_DIR="${JUPYTERLITE_DIR:-$(pwd)}"
PROD="${PROD:-true}"
SKIP_SYNC="${SKIP_SYNC:-false}"
SKIP_LOCAL_BUILD="${SKIP_LOCAL_BUILD:-false}"

cd "$JUPYTERLITE_DIR"

echo "==> Working directory: $(pwd)"

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
  echo "==> Activated .venv"
else
  echo "==> No .venv found. Continuing with current Python environment."
fi

if ! command -v vercel >/dev/null 2>&1; then
  echo "ERROR: vercel CLI not found."
  echo "Install it with: npm i -g vercel"
  exit 1
fi

if ! command -v jupyter >/dev/null 2>&1; then
  echo "ERROR: jupyter command not found in current environment."
  echo "Make sure jupyterlite is installed in your Python environment."
  exit 1
fi

if [ "$SKIP_SYNC" != "true" ] && [ -f "scripts/sync_course_content.py" ]; then
  echo "==> Syncing course content"
  python scripts/sync_course_content.py
fi

if [ "$SKIP_LOCAL_BUILD" != "true" ]; then
  echo "==> Cleaning previous JupyterLite build artifacts"
  rm -rf dist .jupyterlite.doit.db

  echo "==> Building JupyterLite locally"
  jupyter lite build --config jupyter_lite_config.json --output-dir dist
fi

if [ ! -d "dist" ]; then
  echo "ERROR: dist/ folder not found."
  echo "Run a successful local build first."
  exit 1
fi

echo "==> Deploying dist/ to Vercel"
if [ "$PROD" = "true" ]; then
  DEPLOY_URL="$(vercel dist --prod)"
else
  DEPLOY_URL="$(vercel dist)"
fi

echo
echo "==> Deployment complete"
echo "$DEPLOY_URL"

echo "$DEPLOY_URL" > deployment-url.txt
echo "==> Saved deployment URL to deployment-url.txt"

echo
echo "Next checks:"
echo "  1. Open: ${DEPLOY_URL%/}/portal/index.html"
echo "  2. Open: ${DEPLOY_URL%/}/lab/index.html"
echo "  3. Verify backend CORS includes this origin"
