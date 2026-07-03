#!/usr/bin/env bash
# Start the Python Fiddle dev server locally.
# Usage: ./run.sh [port]
#
# Run setup-virtualenv.sh first if you haven't already.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8000}"

# Find the venv: prefer .venv in the repo, then the out-of-repo fallback created
# by setup-virtualenv.sh when the repo is on a read-only filesystem, then .venv310.
if [[ -x "$REPO_DIR/.venv/bin/python" ]]; then
    VENV="$REPO_DIR/.venv"
elif [[ -x "${HOME}/.venvs/pythonfiddle/bin/python" ]]; then
    VENV="${HOME}/.venvs/pythonfiddle"
elif [[ -x "$REPO_DIR/.venv310/bin/python" ]]; then
    VENV="$REPO_DIR/.venv310"
else
    echo "No virtual environment found. Run ./setup-virtualenv.sh first." >&2
    exit 1
fi

TEMPLATES_DIR="${CLOUD_IDE_TEMPLATES_DIR:-$(dirname "$REPO_DIR")/cloud-ide-templates}"
DB_PATH="${DJANGO_DB_PATH:-$REPO_DIR/db.sqlite3}"

echo "Starting Python Fiddle on http://127.0.0.1:$PORT"
echo "  venv:      $VENV"
echo "  templates: $TEMPLATES_DIR"
echo "  database:  $DB_PATH"
echo ""

cd "$REPO_DIR"

CLOUD_IDE_TEMPLATES_DIR="$TEMPLATES_DIR" \
DJANGO_DB_PATH="$DB_PATH" \
  "$VENV/bin/python" manage.py migrate 2>&1 | grep -v "^No migrations to apply"

CLOUD_IDE_TEMPLATES_DIR="$TEMPLATES_DIR" \
DJANGO_DB_PATH="$DB_PATH" \
  exec "$VENV/bin/python" manage.py runserver "$PORT"
