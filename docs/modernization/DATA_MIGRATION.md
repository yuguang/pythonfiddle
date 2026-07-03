# Data Migration

**Status:** Complete — scripts written and roundtrip-tested by Phase 1 (Models + Data) agent.

---

## Overview

The data migration strategy uses standalone export/import scripts rather than Django
migration history. The legacy Django 1.4 project stores data in SQLite (file: `fiddle`,
no extension, in the legacy project root).

Scripts live in `scripts/`. See `scripts/README.md` for full usage documentation.

---

## Legacy → Modern Schema Mapping

| Legacy table | Legacy column | New model field | Notes |
|---|---|---|---|
| `fiddle_language` | `id` | `Language.id` | PK preserved via `get_or_create` |
| `fiddle_language` | `name` | `Language.name` | Used as lookup key |
| `fiddle_snippet` | `id` | _(not preserved)_ | New auto-incremented PK assigned |
| `fiddle_snippet` | `title` | `Snippet.title` | Direct copy |
| `fiddle_snippet` | `slug` | `Snippet.slug` | Re-generated from title on `save()` |
| `fiddle_snippet` | `author_id` | `Snippet.author` | Looked up by username; falls back to `legacy_import_user` |
| `fiddle_snippet` | `description` | `Snippet.description` | Direct copy; empty string if NULL |
| `fiddle_snippet` | `last_modified` | `Snippet.last_modified` | **Not preserved** — `auto_now=True` sets it to import time |
| `fiddle_snippet` | `code` | `Snippet.code` | gzip-decompressed by export script; re-compressed by ORM on import |
| `fiddle_snippet` | `language_id` | `Snippet.language` | Re-linked via `lang_map` (legacy id → new Language object) |
| `taggit_tag` + `taggit_taggeditem` | — | `Snippet.tags` | Re-applied via `snippet.tags.set(tags)` |
| `auth_user` | `username` | Used for author lookup only | Passwords / social auth **not migrated** |

### Tables NOT migrated

| Table | Reason |
|---|---|
| `auth_user` | Passwords are Django-hashed; social auth must be re-linked by users |
| `social_auth_usersocialauth` | OAuth tokens are short-lived; users re-authenticate after launch |
| `django_chunks` | Removed in modernization; templates updated to not use `{% load chunks %}` |

---

## Step-by-step Migration Commands

```bash
# 0. Activate the virtualenv
cd /Users/yuguang/Projects/pythonfiddle-modernize
source .venv/bin/activate

# 1. Ensure the modern DB is fully migrated
python manage.py migrate

# 2. Export from the legacy SQLite DB
#    (legacy DB has no .sqlite extension)
python scripts/export_legacy_data.py ../pythonfiddle/fiddle legacy_export.json

# 3. Verify the export
python -c "
import json
d = json.load(open('legacy_export.json'))
print('Languages:', len(d['languages']), '| Snippets:', len(d['snippets']))
"

# 4. Import into the modern DB
python scripts/import_legacy_data.py legacy_export.json

# 5. Verify the import
python manage.py shell -c "
from cloud_ide.fiddle.models import Snippet, Language
print('Languages:', Language.objects.count())
print('Snippets:', Snippet.objects.count())
"
```

---

## Roundtrip Test (Phase 1 Validation)

The following was run successfully against a fresh `db.sqlite3`:

```bash
# Create test data
python manage.py shell -c "
from cloud_ide.fiddle.models import Language, Snippet
from django.contrib.auth.models import User
u, _ = User.objects.get_or_create(username='testuser')
lang, _ = Language.objects.get_or_create(name='Python')
s = Snippet.objects.create(title='Hello', author=u, language=lang, code='print(\"hello\")')
s.tags.add('test', 'python')
print('Created:', s.id, s.title)
"
python scripts/export_legacy_data.py db.sqlite3 legacy_export.json
python -c "import json; d=json.load(open('legacy_export.json')); print('Languages:', len(d['languages']), 'Snippets:', len(d['snippets']))"
# → Languages: 1 Snippets: 1  ✓
```

Reimport verification (wipe + import):
```bash
python manage.py shell -c "from cloud_ide.fiddle.models import Snippet, Language; Snippet.objects.all().delete(); Language.objects.all().delete()"
python scripts/import_legacy_data.py legacy_export.json
# → Snippets created: 1, Snippets skipped: 0  ✓
# code, tags, author, language all preserved  ✓
```

---

## CompressedTextField Notes

The `code` field uses `CompressedTextField` (`cloud_ide/fiddle/compression.py`) which
gzip-compresses text before storing it as a SQLite `BLOB`.

**Bug fixed in Phase 1:** `get_db_prep_save` was calling `models.TextField.get_db_prep_save`,
which in Python 3 applies `str()` to compressed bytes — storing the repr `b'\x1f\x8b...'`
as TEXT instead of binary. Fixed to return compressed bytes directly.

The export script handles three cases for legacy `code` blobs:
1. **gzip bytes** (standard) — decompressed normally
2. **zlib bytes** (rare legacy variant) — `zlib.decompress` fallback
3. **plain text bytes** (uncompressed rows) — decoded as UTF-8

---

## Open Issues

- `last_modified` timestamps are **not preserved** (`auto_now=True`). Use a raw SQL
  `UPDATE fiddle_snippet SET last_modified = ?` after import if originals are needed.
- `Snippet.slug` has no `unique=True` constraint. Snippets with identical titles get
  the same slug. Evaluate adding uniqueness before launch.
- The placeholder user `legacy_import_user` is created for orphaned snippets.
  Reassign via the Django admin after migrating user accounts.
