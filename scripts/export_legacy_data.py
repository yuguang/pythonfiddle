#!/usr/bin/env python3
"""
Export legacy pythonfiddle SQLite database to a JSON file.

Does NOT require Django to be installed or configured.
Uses the stdlib sqlite3 module directly.

Usage:
    python scripts/export_legacy_data.py [DB_PATH [OUTPUT_PATH]]

    DB_PATH:     Path to the legacy SQLite DB file.
                 Default: ../pythonfiddle/fiddle  (sibling repo, no extension)
    OUTPUT_PATH: Path for the output JSON file.
                 Default: legacy_export.json  (project root)

The code field (CompressedTextField) is stored as a gzip-compressed blob.
This script decompresses it transparently, falling back to zlib and then
raw UTF-8 decode for rows that were stored uncompressed.
"""

import gzip
import io
import json
import os
import sqlite3
import sys
import zlib
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPTS_DIR)

DEFAULT_DB_PATH = os.path.join(_PROJECT_ROOT, '..', 'pythonfiddle', 'fiddle')
DEFAULT_OUTPUT_PATH = os.path.join(_PROJECT_ROOT, 'legacy_export.json')


# ---------------------------------------------------------------------------
# Decompression helpers
# ---------------------------------------------------------------------------

def decompress_code(raw):
    """Decompress a code blob from the legacy DB.

    CompressedTextField stores text as gzip-compressed bytes.
    Legacy rows may have been inserted without compression (plain text bytes
    or actual str if the SQLite driver decoded them).

    Returns a UTF-8 string, or None if *raw* is None.
    """
    if raw is None:
        return None
    if isinstance(raw, str):
        # Already plain text (uncompressed legacy row or already decoded)
        return raw
    if not isinstance(raw, (bytes, bytearray)):
        return str(raw)

    # 1) Try gzip (standard CompressedTextField format)
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as gz:
            return gz.read().decode('utf-8')
    except Exception:
        pass

    # 2) Try zlib (alternative compression sometimes used in older versions)
    try:
        return zlib.decompress(raw).decode('utf-8')
    except Exception:
        pass

    # 3) Plain UTF-8 bytes (uncompressed)
    try:
        return raw.decode('utf-8')
    except Exception:
        pass

    # 4) Latin-1 fallback — lossless decode of arbitrary bytes
    try:
        return raw.decode('latin-1')
    except Exception:
        return repr(raw)


# ---------------------------------------------------------------------------
# Main export
# ---------------------------------------------------------------------------

def export_db(db_path: str, output_path: str) -> None:
    db_path = os.path.abspath(db_path)
    output_path = os.path.abspath(output_path)

    print(f"Source DB:  {db_path}")
    print(f"Output:     {output_path}")

    if not os.path.exists(db_path):
        print(f"ERROR: DB file not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Discover which tables exist
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = {row[0] for row in cur.fetchall()}
    print(f"Tables:     {', '.join(sorted(tables))}")

    # ------------------------------------------------------------------
    # Languages
    # ------------------------------------------------------------------
    languages = []
    if 'fiddle_language' in tables:
        cur.execute("SELECT id, name FROM fiddle_language ORDER BY id")
        for row in cur.fetchall():
            languages.append({'id': row['id'], 'name': row['name']})

    # ------------------------------------------------------------------
    # Snippets (with author username + tags)
    # ------------------------------------------------------------------
    snippets = []
    if 'fiddle_snippet' in tables:
        # Join auth_user to capture author_username for the import script
        if 'auth_user' in tables:
            cur.execute("""
                SELECT s.id,
                       s.title,
                       s.slug,
                       s.author_id,
                       u.username  AS author_username,
                       s.description,
                       s.last_modified,
                       s.code,
                       s.language_id
                FROM fiddle_snippet s
                LEFT JOIN auth_user u ON u.id = s.author_id
                ORDER BY s.id
            """)
        else:
            cur.execute("""
                SELECT id, title, slug, author_id,
                       NULL AS author_username,
                       description, last_modified, code, language_id
                FROM fiddle_snippet
                ORDER BY id
            """)

        for row in cur.fetchall():
            snippet_id = row['id']

            # Resolve tags via taggit tables
            tags = _get_tags_for_snippet(cur, tables, snippet_id)

            # Decompress code blob
            code_text = decompress_code(row['code'])

            snippets.append({
                'id': snippet_id,
                'title': row['title'],
                'slug': row['slug'],
                'author_id': row['author_id'],
                'author_username': row['author_username'],
                'description': row['description'] or '',
                'tags': tags,
                'last_modified': row['last_modified'],
                'code': code_text,
                'language_id': row['language_id'],
            })

    conn.close()

    # ------------------------------------------------------------------
    # Assemble and write JSON
    # ------------------------------------------------------------------
    export_data = {
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'source_db': db_path,
        'row_counts': {
            'languages': len(languages),
            'snippets': len(snippets),
        },
        'languages': languages,
        'snippets': snippets,
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

    print()
    print("Export complete:")
    print(f"  Languages: {len(languages)}")
    print(f"  Snippets:  {len(snippets)}")
    print(f"  Written:   {output_path}")


def _get_tags_for_snippet(cur, tables, snippet_id):
    """Return a list of tag name strings for the given snippet ID."""
    if 'taggit_tag' not in tables or 'taggit_taggeditem' not in tables:
        return []

    # Prefer to filter by content type so we don't cross-contaminate if other
    # taggable models exist.
    if 'django_content_type' in tables:
        try:
            cur.execute("""
                SELECT t.name
                FROM taggit_tag t
                JOIN taggit_taggeditem ti ON ti.tag_id = t.id
                JOIN django_content_type ct ON ct.id = ti.content_type_id
                WHERE ct.model = 'snippet'
                  AND CAST(ti.object_id AS INTEGER) = ?
                ORDER BY t.name
            """, (snippet_id,))
            return [r[0] for r in cur.fetchall()]
        except sqlite3.OperationalError:
            pass  # fall through

    # Fallback: join without content-type filter
    try:
        cur.execute("""
            SELECT t.name
            FROM taggit_tag t
            JOIN taggit_taggeditem ti ON ti.tag_id = t.id
            WHERE CAST(ti.object_id AS INTEGER) = ?
            ORDER BY t.name
        """, (snippet_id,))
        return [r[0] for r in cur.fetchall()]
    except sqlite3.OperationalError:
        return []


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    _db = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB_PATH
    _out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_PATH
    export_db(_db, _out)
