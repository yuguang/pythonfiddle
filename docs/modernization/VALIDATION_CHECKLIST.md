# Validation Checklist — pythonfiddle Django 5.2 Modernization

**Date:** 2026-07-03
**Branch:** `modernize/django5`
**Django:** 5.2.15 / Python 3.14.3

---

## Automated Checks (all PASSED ✅)

| Check | Result |
|-------|--------|
| `manage.py check` | 0 issues |
| `manage.py migrate` | No migrations to apply |
| `GET /` | HTTP 200 (12,416 bytes) |
| `GET /login/` | HTTP 200 (884 bytes) |
| URL reversal — 8 patterns | All PASSED |
| Snippet CRUD + CompressedTextField | PASSED |
| Tags (django-taggit) | PASSED |
| i18n — en + zh activate | PASSED |
| `collectstatic` | 0 errors, 192 files managed |

---

## URL Verification

```
fiddle:create_snippet  →  /
fiddle:save_snippet    →  /save/
fiddle:check_title     →  /check_title/
fiddle:tag_hint        →  /tag_hint/
fiddle:open_snippet    →  /hello/
login                  →  /login/
logout                 →  /logout/
set_language           →  /i18n/setlang/
```

---

## Manual Pre-Cutover Checklist

- [ ] Home page loads — fiddle editor visible
- [ ] Code editor accepts input (CodeMirror)
- [ ] Run button executes Python code (browser-side JS interpreter)
- [ ] Save fiddle — creates a Snippet, redirects to `/<slug>/`
- [ ] Open saved fiddle — code pre-populated
- [ ] Embedded view — toolbar hidden
- [ ] Login page — social auth links present
- [ ] Language switch — English ↔ Chinese
- [ ] Static assets load (CSS, JS, favicon, logo)
- [ ] Admin accessible with superuser

---

## Cutover Runbook

### 1. Export production data
```bash
python scripts/export_legacy_data.py /path/to/production.db legacy_export.json
```

### 2. Deploy, configure env vars, migrate
```bash
git clone -b modernize/django5 https://github.com/yuguang/pythonfiddle.git
pip install -r requirements.txt && pip install -e /path/to/django-cloud-ide
export SECRET_KEY=<key> GOOGLE_KEY=<key> GOOGLE_SECRET=<secret>  # etc.
python manage.py migrate
python scripts/import_legacy_data.py legacy_export.json
python manage.py collectstatic --noinput
```

### 3. Start production server
```bash
gunicorn pythonfiddle_modern.wsgi:application --bind 0.0.0.0:8000
```

### 4. Switch DNS / verify / rollback if needed

---

## Known Limitations / Deferred Work

1. OAuth credentials must be set via env vars before social login works
2. `cloud_ide.snippet` and `cloud_ide.shared` apps not ported (author pages, tag listings)
3. `SITE_ID` must be set correctly for flatpages in production
4. Python runtime in the browser (Skulpt) runs client-side — verify JS assets load

# ORIGINAL PLACEHOLDER BELOW (superseded)

**Status:** Placeholder — to be filled by Phase 6 (Validation) agent.

---

## Smoke Tests

| Test | Expected | Status |
|------|----------|--------|
| `python manage.py migrate` | Exits 0, all migrations applied | [ ] |
| `python manage.py runserver` starts | No ImportError, "Starting development server" | [ ] |
| Home page (`/`) loads | HTTP 200 | [ ] |
| New fiddle page loads | HTTP 200, editor visible | [ ] |
| Save fiddle (POST `/save/`) | Returns JSON `{success: true}` | [ ] |
| Open existing fiddle | HTTP 200, code populated | [ ] |
| Login page (`/login/`) | HTTP 200 | [ ] |
| Google OAuth redirect | Redirects to Google | [ ] |
| Twitter OAuth redirect | Redirects to Twitter | [ ] |
| Facebook OAuth redirect | Redirects to Facebook | [ ] |
| Language switch (en ↔ zh) | UI text changes language | [ ] |
| Admin (`/admin/`) | HTTP 200, login works | [ ] |
| `collectstatic` | Exits 0, files in staticfiles/ | [ ] |

## Data Migration Verification

| Test | Expected | Status |
|------|----------|--------|
| Export runs without error | Produces export file | [ ] |
| Import on clean DB succeeds | Exits 0 | [ ] |
| Snippet count matches | Row count within tolerance | [ ] |
| Language count matches | All languages present | [ ] |
| Sample fiddle renders | Code field decompresses correctly | [ ] |

## Cutover Runbook

(To be written by Validation agent after all other phases complete.)

1. Export data from production
2. Deploy new codebase
3. Import data
4. DNS / load balancer switch
5. Rollback plan
