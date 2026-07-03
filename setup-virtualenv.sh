#!/usr/bin/env bash
# setup-virtualenv.sh — first-time dev environment setup for pythonfiddle-modernize
#
# Usage:
#   ./setup-virtualenv.sh              # full setup (venv + deps + migrate)
#   ./setup-virtualenv.sh --only-deps  # reinstall deps into existing venv
#   ./setup-virtualenv.sh --help
#
# What this script does:
#   1. Creates .venv using Python 3 (3.11+ recommended, 3.10+ required)
#   2. Clones sibling repos (django-cloud-ide, cloud-ide-templates) if absent
#   3. pip install -r requirements.txt
#   4. pip install -e ../django-cloud-ide  (editable, so edits take effect immediately)
#   5. python manage.py migrate
#
# Environment variables (all optional):
#   PYTHON         path to python3 binary  (default: auto-detected)
#   DJANGO_DB_PATH path to sqlite3 DB file (default: db.sqlite3 in project root)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$REPO_DIR")"
VENV="$REPO_DIR/.venv"

CLOUD_IDE_DIR="${CLOUD_IDE_DIR:-$PARENT_DIR/django-cloud-ide}"
TEMPLATES_DIR="${CLOUD_IDE_TEMPLATES_DIR:-$PARENT_DIR/cloud-ide-templates}"
DB_PATH="${DJANGO_DB_PATH:-$REPO_DIR/db.sqlite3}"

ONLY_DEPS=false

# ── argument parsing ──────────────────────────────────────────────────────────
usage() {
    cat <<EOF
Usage: setup-virtualenv.sh [options]

Options:
  -h, --help        Show this help and exit
  -d, --only-deps   Skip venv creation; reinstall deps into existing .venv
EOF
}

for arg in "$@"; do
    case "$arg" in
        -h|--help)   usage; exit 0 ;;
        -d|--only-deps) ONLY_DEPS=true ;;
        *) echo "Unknown option: $arg" >&2; usage >&2; exit 1 ;;
    esac
done

# ── helpers ───────────────────────────────────────────────────────────────────
info()    { echo "  $*"; }
section() { echo ""; echo "==> $*"; }
die()     { echo "ERROR: $*" >&2; exit 1; }

# ── 1. find python3 ───────────────────────────────────────────────────────────
section "Checking Python"

if [[ -n "${PYTHON:-}" ]]; then
    PY="$PYTHON"
else
    for candidate in python3.12 python3.11 python3.10 python3; do
        if command -v "$candidate" &>/dev/null; then
            PY="$(command -v "$candidate")"
            break
        fi
    done
fi

[[ -n "${PY:-}" ]] || die "Python 3.10+ not found. Install it or set PYTHON=/path/to/python3."

PY_VER=$("$PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
info "Using $PY ($PY_VER)"

# Require at least 3.10
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' \
    || die "Python 3.10+ required (got $PY_VER)"

# ── helpers: create a venv robustly ──────────────────────────────────────────
# Some environments (Debian/Ubuntu without python3-venv, or stripped Docker
# images) don't have ensurepip. We try the normal path first and fall back to
# --without-pip + bootstrapping pip from the system pip.
make_venv() {
    local target="$1"
    if "$PY" -m venv "$target" 2>/dev/null; then
        return 0
    fi
    info "ensurepip unavailable — creating venv without pip and bootstrapping manually"
    "$PY" -m venv --without-pip "$target"
    # Bootstrap: copy pip from the system into the new venv's site-packages
    local site
    site=$("$target/bin/python" -c "import site; print(site.getsitepackages()[0])")
    python3 -m pip install --quiet --target="$site" pip setuptools wheel
}

# ── 2. create venv ────────────────────────────────────────────────────────────
if [[ "$ONLY_DEPS" == false ]]; then
    section "Creating virtual environment at .venv"
    if [[ -x "$VENV/bin/python" ]]; then
        info ".venv already exists and is healthy — skipping creation (use --only-deps to just reinstall deps)"
    else
        if [[ -d "$VENV" ]]; then
            info ".venv directory exists but Python binary is missing or broken"
            # Try --clear first; if the directory is on a read-only mount, fall
            # back to a writable sibling directory instead.
            if "$PY" -m venv --clear "$VENV" 2>/dev/null || \
               "$PY" -m venv --without-pip --clear "$VENV" 2>/dev/null; then
                info "Cleared and recreated $VENV"
                # Re-bootstrap pip if needed
                [[ -x "$VENV/bin/pip" ]] || {
                    local site
                    site=$("$VENV/bin/python" -c "import site; print(site.getsitepackages()[0])")
                    python3 -m pip install --quiet --target="$site" pip setuptools wheel
                }
            else
                # The repo directory itself is read-only (e.g. a sandbox mount).
                # Fall back to a venv outside the repo.
                VENV="${HOME}/.venvs/pythonfiddle"
                info "Cannot modify $REPO_DIR/.venv (read-only filesystem)"
                info "Creating venv outside the repo at $VENV"
                mkdir -p "$(dirname "$VENV")"
                make_venv "$VENV"
            fi
        else
            make_venv "$VENV"
        fi
        info "Created $VENV"
    fi
fi

# If the primary venv path is broken, check the fallback location before giving up
if [[ ! -x "$VENV/bin/python" ]] && [[ -x "${HOME}/.venvs/pythonfiddle/bin/python" ]]; then
    VENV="${HOME}/.venvs/pythonfiddle"
fi
[[ -x "$VENV/bin/python" ]] || die "No working venv found at $VENV. Run without --only-deps to create it."
PIP="$VENV/bin/pip"

# ── 3. clone sibling repos if absent ─────────────────────────────────────────
section "Checking sibling repositories"

if [[ ! -d "$CLOUD_IDE_DIR" ]]; then
    info "Cloning django-cloud-ide into $CLOUD_IDE_DIR"
    git clone https://github.com/yuguang/django-cloud-ide.git "$CLOUD_IDE_DIR"
else
    info "django-cloud-ide already present at $CLOUD_IDE_DIR"
fi

if [[ ! -d "$TEMPLATES_DIR" ]]; then
    info "Cloning cloud-ide-templates into $TEMPLATES_DIR"
    git clone https://github.com/yuguang/cloud-ide-templates.git "$TEMPLATES_DIR"
else
    info "cloud-ide-templates already present at $TEMPLATES_DIR"
fi

# ── 4. install dependencies ───────────────────────────────────────────────────
section "Installing Python dependencies"

"$PIP" install --upgrade pip --quiet
"$PIP" install -r "$REPO_DIR/requirements.txt"

info "Installing django-cloud-ide as editable package"
"$PIP" install -e "$CLOUD_IDE_DIR"

# ── 5. run migrations ─────────────────────────────────────────────────────────
section "Running database migrations"

cd "$REPO_DIR"
CLOUD_IDE_TEMPLATES_DIR="$TEMPLATES_DIR" \
DJANGO_DB_PATH="$DB_PATH" \
    "$VENV/bin/python" manage.py migrate

# ── done ──────────────────────────────────────────────────────────────────────
echo ""
echo "Setup complete. Start the dev server with:"
echo ""
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  source $VENV/bin/activate"
echo "  CLOUD_IDE_TEMPLATES_DIR=$TEMPLATES_DIR python manage.py runserver"
echo ""
