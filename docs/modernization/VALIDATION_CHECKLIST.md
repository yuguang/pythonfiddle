# Validation Checklist

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
