#!/usr/bin/env bash
set -e

while true; do
  echo "[worker] running pending grading jobs"
  python -m app.workers.grading_jobs --pending --limit 20 || true

  echo "[worker] running expiry check"
  python -m app.workers.grading_jobs --expiry-check || true

  echo "[worker] sleeping for 30 seconds"
  sleep 30
done
