# Frontend API Integration Guide

> **Backend Version**: As of 2026-01-30  
> **Status**: Local testing ✅ | GCP Config Needs Fix ⚠️

---

## Quick Summary

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/v1/tasks` | GET | ✅ Working | Returns `[]` for new offices |
| `/api/v1/tasks/{id}` | GET | ✅ Working (NEW) | Added 2026-01-30 |
| `/api/v1/patients` | GET | ✅ Working | Decrypts names automatically |
| `/api/v1/visits/schedule` | GET | ✅ Working | Requires `?date=YYYY-MM-DD` |
| `/api/v1/auth/keys` | GET | ✅ Exists | Lists API keys for office |

---

## Authentication

### Using Bearer Token (Recommended for Frontend)
```javascript
// After login, store the token
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { access_token } = await response.json();

// Use in subsequent requests
fetch('/api/v1/tasks', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

### Using API Key (For Server-to-Server)
```javascript
fetch('/api/v1/tasks', {
  headers: { 'X-Office-Key': 'sk_live_...' }
});
```

---

## Common Issues & Solutions

### 1. "Could not validate credentials" (403)

**Cause**: Usually means the auth header is missing or malformed.

**Checklist**:
- [ ] Verify `Authorization: Bearer <token>` header is present
- [ ] No extra spaces: `Bearer <token>` not `Bearer  <token>`
- [ ] Token is not expired (8 days default)
- [ ] Check browser DevTools → Network tab → verify header is actually sent

**JavaScript Bug Pattern**:
```javascript
// ❌ WRONG - headers in wrong position
axios.get(url, { data: params }, { headers: {...} })

// ✅ CORRECT
axios.get(url, { headers: {...}, params: {...} })
```

### 2. "405 Method Not Allowed"

**Cause**: Wrong URL or trailing slash.

**Checklist**:
- [ ] No trailing slash: `/api/v1/tasks` not `/api/v1/tasks/`
- [ ] Correct path (e.g., `/tasks` not `/task`)
- [ ] For detail views: `/tasks/{uuid}` not `/tasks?id=uuid`

### 3. "Internal Server Error" on GCP

**Current Status**: GCP Cloud Run has mis-configured env vars.  
**Workaround**: Use local development until GCP is fixed.  
**Root Cause**: `cloudbuild.yaml` was overwriting `DB_USER` incorrectly.

---

## Endpoints Reference

### GET /api/v1/tasks
```
Query Params:
  - status (optional): "PENDING" | "COMPLETED" | "DISMISSED"
  - limit (optional): 1-100, default 50
  - offset (optional): default 0

Response: TaskResponse[]
```

### GET /api/v1/patients
```
Query Params:
  - limit (optional): 1-100, default 50
  - offset (optional): default 0

Response: PatientResponse[] (names auto-decrypted)
```

### GET /api/v1/visits/schedule
```
Query Params:
  - date (required): YYYY-MM-DD format (interpreted as UTC)

Response: VisitResponse[]
```

### GET /api/v1/notes/patient/{patient_id}
```
Path Params:
  - patient_id (required): UUID

Response: NoteResponse[]
```

### GET /api/v1/auth/keys
```
Auth: Bearer token required (ADMIN)

Response: ApiKeyResponse[]
```

---

## Timezone Handling

All timestamps are stored and returned in **UTC**. See `/docs/TIMEZONE_HANDLING.md` for details.

**Frontend Responsibility**:
1. Convert user-selected times to UTC before sending to API
2. Convert UTC responses to local time for display
3. For `/visits/schedule`: send UTC date, filter results client-side if needed

---

## What Was Fixed (2026-01-30)

1. **Added `GET /tasks/{task_id}`** - Was missing, caused 405 on task detail fetch
2. **Corrected `cloudbuild.yaml`** - Fixed `DB_USER=postgres` → `dental_user`
3. **Documented timezone handling** - Created `/docs/TIMEZONE_HANDLING.md`
4. **Verified endpoints locally** - All return 200 OK with valid auth
