# Data Migration

**Status:** Placeholder — to be filled by Phase 1 (Models + Data) agent.

---

## Overview

The data migration strategy for pythonfiddle uses export/import scripts rather than
Django migration history. The legacy Django 1.4 project stores data in SQLite (file: `fiddle`
with no extension).

## Legacy Schema

Run `python manage.py inspectdb` against the legacy DB to get the raw table definitions.
See `old_inspectdb.txt` in this directory.

## Tables to Migrate

| Legacy table | New model | Notes |
|---|---|---|
| `fiddle_language` | `cloud_ide.fiddle.Language` | Simple lookup table |
| `fiddle_snippet` | `cloud_ide.fiddle.Snippet` | `code` field is gzip-compressed blob |
| `taggit_tag` | `taggit.Tag` | Shared via django-taggit |
| `taggit_taggeditem` | `taggit.TaggedItem` | Content type mapping will change |
| `auth_user` | `auth.User` | Passwords are Django hashed; social accounts via social_django |
| `social_auth_usersocialauth` | `social_django.UserSocialAuth` | OAuth tokens |

## Export Script

**Path:** `scripts/export_legacy_data.py` (to be created by Phase 1 agent)

Pseudocode:
```
connect to legacy SQLite DB
for each table: dump rows to JSON
handle CompressedTextField: decompress blob to plaintext before export
write output to data/legacy_export.json.gz
```

## Import Script

**Path:** `scripts/import_to_modern.py` (to be created by Phase 1 agent)

Pseudocode:
```
read data/legacy_export.json.gz
for each Language: get_or_create
for each Snippet: create with author lookup, tag restoration
log any rows that fail (orphaned FKs, missing authors)
```

## Verification

After import, run:
```bash
python manage.py shell -c "
from cloud_ide.fiddle.models import Snippet, Language
print(f'Languages: {Language.objects.count()}')
print(f'Snippets: {Snippet.objects.count()}')
"
```

## Open Issues

- Legacy `code` blob may be compressed or uncompressed depending on how the record was created.
- The `author` FK is required in the new schema; orphaned snippets need a placeholder user.
- `django-chunks` content (flatpage-like text fragments) has no direct equivalent; evaluate whether needed.
