# Migration Scripts

These scripts migrate data from the legacy Django 1.4 pythonfiddle SQLite database
into the modern Django 5.2 schema.

---

## export_legacy_data.py

Reads the legacy SQLite DB and writes a portable JSON file.  
**Does not require Django** — uses `sqlite3` from the standard library.

### Usage

```bash
# From the project root (venv active)
python scripts/export_legacy_data.py [DB_PATH [OUTPUT_PATH]]
```

| Argument | Default | Description |
|---|---|---|
| `DB_PATH` | `../pythonfiddle/fiddle` | Path to the legacy SQLite file (no `.sqlite` extension in legacy repo) |
| `OUTPUT_PATH` | `legacy_export.json` | Output JSON file |

### Example

```bash
# Export from the legacy repo sibling directory
python scripts/export_legacy_data.py ../pythonfiddle/fiddle legacy_export.json

# Export from an explicit dump
python scripts/export_legacy_data.py /tmp/prod_backup.sqlite legacy_export.json
```

### Output format

```json
{
  "exported_at": "2026-06-13T23:00:00+00:00",
  "source_db": "/path/to/fiddle",
  "row_counts": { "languages": 5, "snippets": 1234 },
  "languages": [
    { "id": 1, "name": "python" }
  ],
  "snippets": [
    {
      "id": 1,
      "title": "Hello World",
      "slug": "hello-world",
      "author_id": 3,
      "author_username": "alice",
      "description": "",
      "tags": ["demo", "python"],
      "last_modified": "2014-03-01 10:00:00",
      "code": "print('hello')",
      "language_id": 1
    }
  ]
}
```

### CompressedTextField handling

The `code` column is stored as a **gzip-compressed blob** by `CompressedTextField`.
The export script tries decompression in this order:

1. **gzip** (standard, used by `compress_string` in `compression.py`)
2. **zlib** (fallback for alternate legacy encoding)
3. **UTF-8 bytes** (uncompressed rows)
4. **Latin-1** (byte-safe fallback)

---

## import_legacy_data.py

Reads `legacy_export.json` and populates the Django DB via the ORM.  
**Requires Django** — run from the project root with the virtualenv active.

### Usage

```bash
# From the project root (venv active)
python scripts/import_legacy_data.py [INPUT_PATH]
```

| Argument | Default | Description |
|---|---|---|
| `INPUT_PATH` | `legacy_export.json` | JSON file produced by the export script |

### Example

```bash
python scripts/import_legacy_data.py legacy_export.json
```

### Behaviour

| Object | Strategy |
|---|---|
| `Language` | `get_or_create` by `name` |
| `Snippet` | `create` (see warning below) |
| Author lookup | Username first, then numeric id; falls back to `legacy_import_user` |
| Tags | `snippet.tags.set(*tags)` after creation |

> **Warning:** Running this script twice will create duplicate snippets.
> Clear the snippet and language tables before re-running:
> ```bash
> python manage.py shell -c "
> from cloud_ide.fiddle.models import Snippet, Language
> Snippet.objects.all().delete()
> Language.objects.all().delete()
> "
> ```

### Skipped rows

Any row that cannot be imported (missing language reference, unexpected exception)
is logged as a warning and listed in the summary at the end.

---

## Full roundtrip example

```bash
# 1. Activate virtualenv
source .venv/bin/activate

# 2. Ensure migrations are applied
python manage.py migrate

# 3. Seed test data
python manage.py shell -c "
from cloud_ide.fiddle.models import Language, Snippet
from django.contrib.auth.models import User
u, _ = User.objects.get_or_create(username='testuser')
lang, _ = Language.objects.get_or_create(name='Python')
s = Snippet.objects.create(title='Hello', author=u, language=lang, code='print(\"hello\")')
s.tags.add('demo', 'python')
print('Created snippet id:', s.id)
"

# 4. Export
python scripts/export_legacy_data.py db.sqlite3 legacy_export.json

# 5. Verify export
python -c "
import json
d = json.load(open('legacy_export.json'))
print('Languages:', len(d['languages']), 'Snippets:', len(d['snippets']))
"

# 6. (Optional) wipe and re-import into a fresh DB
python manage.py shell -c "
from cloud_ide.fiddle.models import Snippet, Language
Snippet.objects.all().delete(); Language.objects.all().delete()
"
python scripts/import_legacy_data.py legacy_export.json

# 7. Verify import
python manage.py shell -c "
from cloud_ide.fiddle.models import Snippet, Language
print('Languages:', Language.objects.count())
print('Snippets:', Snippet.objects.count())
"
```
