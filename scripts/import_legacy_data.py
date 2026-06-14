#!/usr/bin/env python3
"""
Import legacy pythonfiddle data from a JSON export file into the modern Django DB.

Requires the Django project to be on PYTHONPATH (run from project root).

Usage:
    python scripts/import_legacy_data.py [INPUT_PATH]

    INPUT_PATH: Path to the JSON export file produced by export_legacy_data.py
                Default: legacy_export.json  (project root)

Behaviour:
  - Language  → get_or_create by name
  - Snippet   → created fresh; if the author_id/username does not exist in the
                new DB a placeholder user ("legacy_import_user") is used instead
  - Tags      → re-applied via snippet.tags.set()
  - Skipped rows are logged with a reason; a summary is printed at the end

WARNING: Running this script against a DB that already contains snippet data
will create duplicate snippets.  Clear the snippet / language tables before
re-running if you need a clean import.
"""

import json
import logging
import os
import sys

# ---------------------------------------------------------------------------
# Bootstrap Django
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPTS_DIR)
sys.path.insert(0, _PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pythonfiddle_modern.settings')

import django  # noqa: E402
django.setup()

from django.contrib.auth.models import User          # noqa: E402
from cloud_ide.fiddle.models import Language, Snippet  # noqa: E402

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_INPUT_PATH = os.path.join(_PROJECT_ROOT, 'legacy_export.json')
PLACEHOLDER_USERNAME = 'legacy_import_user'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_placeholder_user():
    """Return (and lazily create) the fallback author for orphaned snippets."""
    user, created = User.objects.get_or_create(
        username=PLACEHOLDER_USERNAME,
        defaults={'email': 'legacy@pythonfiddle.example', 'is_active': True},
    )
    if created:
        log.info("Created placeholder user: %s", PLACEHOLDER_USERNAME)
    return user


# ---------------------------------------------------------------------------
# Main import
# ---------------------------------------------------------------------------

def import_data(input_path: str) -> None:
    input_path = os.path.abspath(input_path)
    log.info("Reading: %s", input_path)

    if not os.path.exists(input_path):
        log.error("Input file not found: %s", input_path)
        sys.exit(1)

    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)

    log.info("Source DB:   %s", data.get('source_db', 'unknown'))
    log.info("Exported at: %s", data.get('exported_at', 'unknown'))
    log.info("Expected:    %s languages, %s snippets",
             data['row_counts']['languages'], data['row_counts']['snippets'])

    # ------------------------------------------------------------------
    # 1. Languages — get_or_create by name
    # ------------------------------------------------------------------
    lang_map: dict[int, Language] = {}  # legacy id → new Language object
    lang_created = lang_existing = 0

    for rec in data.get('languages', []):
        lang, created = Language.objects.get_or_create(name=rec['name'])
        lang_map[rec['id']] = lang
        if created:
            lang_created += 1
            log.info("  [lang] Created: %s", lang.name)
        else:
            lang_existing += 1

    log.info("Languages: %d created, %d already existed", lang_created, lang_existing)

    # ------------------------------------------------------------------
    # 2. Snippets
    # ------------------------------------------------------------------
    snippet_created = 0
    snippet_skipped = 0
    skipped: list[str] = []
    placeholder: User | None = None

    for rec in data.get('snippets', []):
        legacy_id = rec.get('id', '?')
        title = rec.get('title', '')

        # Resolve language
        language = lang_map.get(rec.get('language_id'))
        if language is None:
            reason = (
                f"id={legacy_id} title='{title}': "
                f"language_id={rec.get('language_id')} not found in export"
            )
            log.warning("SKIP: %s", reason)
            skipped.append(reason)
            snippet_skipped += 1
            continue

        # Resolve author — try by id then by username, fall back to placeholder
        author = _resolve_author(rec)
        if author is None:
            if placeholder is None:
                placeholder = _get_placeholder_user()
            author = placeholder
            log.warning(
                "  [snippet] id=%s '%s': author not found (id=%s, username=%s) "
                "→ placeholder",
                legacy_id, title, rec.get('author_id'), rec.get('author_username'),
            )

        # Create the snippet
        code = rec.get('code') or ''
        try:
            snippet = Snippet.objects.create(
                title=title,
                author=author,
                description=rec.get('description') or '',
                code=code,
                language=language,
            )
            # Re-apply tags
            tags = rec.get('tags') or []
            if tags:
                snippet.tags.set(tags)
            snippet_created += 1
            log.info("  [snippet] Created: '%s' [%s] tags=%s", title, language.name, tags)

        except Exception as exc:
            reason = f"id={legacy_id} title='{title}': {exc}"
            log.error("SKIP (error): %s", reason)
            skipped.append(reason)
            snippet_skipped += 1

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    print("=" * 40)
    print("Import summary")
    print("=" * 40)
    print(f"  Languages total:   {Language.objects.count()}")
    print(f"  Snippets total:    {Snippet.objects.count()}")
    print(f"  Snippets created:  {snippet_created}")
    print(f"  Snippets skipped:  {snippet_skipped}")
    if skipped:
        print()
        print("Skipped rows:")
        for reason in skipped:
            print(f"  • {reason}")


def _resolve_author(rec: dict):
    """Try to find an existing User; return None if not found."""
    # 1) Look up by username (most reliable cross-DB)
    username = rec.get('author_username')
    if username:
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            pass

    # 2) Fall back to numeric id (only useful if user table was also migrated)
    author_id = rec.get('author_id')
    if author_id is not None:
        try:
            return User.objects.get(id=author_id)
        except User.DoesNotExist:
            pass

    return None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    _inp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT_PATH
    import_data(_inp)
