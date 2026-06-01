#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# jupyterlite-xeus may need micromamba available on PATH depending on platform.
if ! command -v micromamba >/dev/null 2>&1; then
  echo "micromamba not found. Install it first if jupyterlite-xeus build asks for it."
fi
