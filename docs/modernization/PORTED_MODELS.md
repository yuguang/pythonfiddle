# Ported Models

Documented by Phase 0 (Scaffolding) agent.  
Source: `/Users/yuguang/Projects/django-cloud-ide/cloud_ide/fiddle/models.py`

---

## Package: `cloud_ide.fiddle`

### `Language`

| Field | Type | Notes |
|-------|------|-------|
| `id` | AutoField (implicit) | PK |
| `name` | CharField(max_length=30) | Language slug (e.g. "python", "javascript") |

**Methods:**
- `get_absolute_url()` → reverse `fiddle_language_detail`
- `__str__()` → `self.name`

---

### `Snippet`

| Field | Type | Notes |
|-------|------|-------|
| `id` | AutoField (implicit) | PK |
| `title` | CharField(max_length=80) | Translated label: "Title" |
| `slug` | SlugField(max_length=100) | Auto-generated from title on save |
| `author` | ForeignKey(User, CASCADE) | Django auth User |
| `description` | CharField(max_length=300) | Translated label: "Description" |
| `tags` | TaggableManager | via django-taggit |
| `last_modified` | DateTimeField(auto_now=True) | Updated on every save |
| `code` | CompressedTextField | gzip-compressed text field (blob in DB) |
| `language` | ForeignKey(Language, PROTECT) | Can't delete a Language with associated Snippets |

**Meta:**
- `ordering = ('-last_modified',)` — newest first

**Methods:**
- `save()` — auto-slugifies title
- `get_tagstring()` — comma-separated tag names
- `get_absolute_url()` — `/{language}/{slug}/` (multi-language) or `/{slug}/` (single)
- `__str__()` → `self.title`

**Manager: `SnippetManager`**
- `top_authors()` — Users annotated with snippet count, ordered by score
- `top_tags()` — most common tags
- `matches_tag(tag)` — filter by tag

---

## `CompressedTextField`

Custom `TextField` subclass in `cloud_ide/fiddle/compression.py`.

- Stores text as gzip-compressed bytes (`blob` type in SQLite, `longblob` in MySQL)
- Transparently compresses on `get_db_prep_save`
- Decompresses on `post_init` signal

**Django 5 changes applied:**
- Removed Python 2 `cStringIO` → `io.BytesIO`
- Removed `django.utils.text.compress_string` (dropped in Django 2.0) → local `compress_string` using `gzip`
- Fixed Python 2 `raise Exception, msg` syntax → `raise Exception(msg)`

---

## Module-level constants (in `models.py`)

These are template context defaults also defined in `models.py`:

- `defaultFiddle` — `{'newFiddle': True, 'isOwner': True}`
- `defaultMeta` — SEO defaults (title, description, keywords)
- `languageMeta` — per-language SEO metadata dict (python, coffeescript, typescript, jsx, js, sass, scss, less, css, html, haml, jade, etc.)

---

## Python 2 → Python 3 / Django 1.4 → Django 5.2 Changes

| File | Change |
|------|--------|
| `compression.py` | `cStringIO` → `io`; removed `django.utils.text.compress_string`; fixed exception syntax |
| `models.py` | `from compression import` → `from cloud_ide.fiddle.compression import`; `ugettext_lazy` → `gettext_lazy`; `@permalink` → `reverse()`; added `on_delete` to ForeignKeys; `__unicode__` → `__str__` |
| `forms.py` | `from models import *` → `from cloud_ide.fiddle.models import Snippet` |
| `admin.py` | `from models import Snippet` → `from cloud_ide.fiddle.models import Snippet` |
| `views.py` | `render_to_response`+`RequestContext` → `render`; `is_authenticated()` → `.is_authenticated`; `is_ajax()` → header check; `simplejson` → stdlib `json`; `mimetype` → `content_type` |
| `jsonresponse.py` | `simplejson` → Django's `JsonResponse` |
| `templatetags/jqtmpl.py` | `TOKEN_BLOCK`/`TOKEN_VAR` → `TokenType.BLOCK`/`TokenType.VAR`; `TextNode` from `django.template.base` |

---

## Open Questions for Models Agent (Phase 1)

1. **CompressedTextField migration**: The initial migration stores `code` as `BlobField` (`blob` in SQLite). Existing data from the legacy DB may be gzip-compressed bytes or plain text. The export script must handle both.
2. **Language seeding**: There is no fixture for `Language` records. The models agent should create initial data for common languages (python, javascript, etc.).
3. **Snippet.slug uniqueness**: The current model has no `unique=True` on `slug`. Two snippets with the same title would get the same slug. Consider adding `unique=True` or making it `unique_for_date`.
4. **Snippet.author nullable**: Currently `author` is non-nullable. For imported snippets whose author account doesn't exist in the new DB, a fallback user or null author is needed.
