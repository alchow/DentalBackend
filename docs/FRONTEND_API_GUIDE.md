# Frontend API Integration Guide

> **Backend Version**: As of 2026-02-02  
> **Status**: GCP ✅ | All E2E Tests Passing | AI Summaries ✅

---

## Quick Summary

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/v1/notes` | GET | ✅ Working | List all notes with pagination |
| `/api/v1/notes/{id}` | GET | ✅ Working | Get single note by ID |
| `/api/v1/notes/patient/{id}` | GET | ✅ Working | Notes for a specific patient |
| `/api/v1/patients/{id}/summary` | GET | ✅ Working | AI-generated patient summary |
| `/api/v1/tasks` | GET | ✅ Working | Returns `[]` for new offices |
| `/api/v1/tasks/{id}` | GET | ✅ Working | Added 2026-01-30 |
| `/api/v1/patients` | GET | ✅ Working | Decrypts names automatically |
| `/api/v1/visits/schedule` | GET | ✅ Working | Requires `?date=YYYY-MM-DD` |
| `/api/v1/search` | POST | ✅ Working | Full-text + semantic search |

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

**Current Status**: ✅ RESOLVED (as of 2026-02-02)  
**Root Cause**: Fixed `cloudbuild.yaml` DB_USER and verified summary pipeline.

---

## Endpoints Reference

### GET /api/v1/tasks
```
Query Params:
  - status (optional): "PENDING" | "COMPLETED" | "DISMISSED"
  - assignee_type (optional): "DENTIST" | "PATIENT" | "FRONT_DESK"
  - limit (optional): 1-100, default 50
  - offset (optional): default 0

Response: TaskResponse[]
```

**TaskResponse Schema:**
```typescript
interface TaskResponse {
  id: string;
  patient_id: string;
  description: string;
  status: "PENDING" | "COMPLETED" | "DISMISSED";
  priority: "HIGH" | "NORMAL";
  due_date: string | null;    // YYYY-MM-DD
  assignee_type: "DENTIST" | "PATIENT" | "FRONT_DESK";
  generated_by: string | null; // "LLM" or "User"
  created_at: string;
  updated_at: string;
}
```

**Example - Get patient-facing tasks:**
```javascript
const response = await fetch(
  '/api/v1/tasks?assignee_type=PATIENT&status=PENDING',
  { headers: { 'Authorization': `Bearer ${token}` }}
);
```

### GET /api/v1/patients
```
Query Params:
  - limit (optional): 1-100, default 50
  - offset (optional): default 0

Response: PatientResponse[] (names auto-decrypted)
```

### GET /api/v1/patients/{patient_id}/summary
*Retrieve the AI-generated patient summary for pre-visit huddles.*

```
Path Params:
  - patient_id (required): UUID

Response: SummaryResponse
Error: 404 if no summary exists yet
```

> **Note**: Summaries are automatically generated via Cloud Tasks when clinical notes are created. LLM generation takes ~10 seconds. Poll after creating a note if you need the summary immediately.

**SummaryResponse Schema:**
```typescript
interface SummaryResponse {
  id: string;
  patient_id: string;
  content: {
    summary_markdown: string;      // Human-readable narrative
    chief_concerns: string[];
    ongoing_treatment: string | null;
    key_clinical_findings: string[];
    action_items: string[];
    risk_factors: string[];
  };
  source: "AI" | "MANUAL";
  model_name: string;              // e.g., "gpt-4o-mini"
  confidence_score: number;        // 0.0-1.0
  created_at: string;
}
```

**Example:**
```javascript
const response = await fetch(
  `/api/v1/patients/${patientId}/summary`,
  { headers: { 'X-Office-Key': 'sk_live_...' }}
);
if (response.status === 404) {
  // No summary yet - show placeholder or trigger generation
}
```

### GET /api/v1/visits/schedule
```
Query Params:
  - date (required): YYYY-MM-DD format (interpreted as UTC)

Response: VisitResponse[]
```

### GET /api/v1/notes
*List all clinical notes for your office with filtering and pagination.*

```
Query Params:
  - limit (optional): 1-100, default 50
  - offset (optional): default 0
  - sort (optional): "created_at" | "updated_at", default "created_at"
  - order (optional): "asc" | "desc", default "desc"
  - note_type (optional): "CHART" | "TREATMENT" | "FINDING" | etc.
  - patient_id (optional): UUID - filter to specific patient
  - visit_id (optional): UUID - filter to specific visit
  - date_from (optional): ISO8601 - notes created after this date
  - date_to (optional): ISO8601 - notes created before this date
  - include_patient (optional): boolean, default false

Response (Paginated):
{
  "items": [NoteResponse],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

**Example Request:**
```javascript
// Get recent chart notes with patient info
const response = await fetch(
  '/api/v1/notes?limit=20&note_type=CHART&include_patient=true',
  { headers: { 'Authorization': `Bearer ${token}` }}
);
const { items, total } = await response.json();
// items[0].patient.first_name is available
```

**NoteResponse Schema:**
```typescript
interface NoteResponse {
  id: string;           // UUID
  patient_id: string;   // UUID
  visit_id: string | null;
  content: string;      // Decrypted automatically
  tooth_number: string | null;
  surface_ids: string | null;
  area_of_oral_cavity: string | null;
  note_type: string;    // "CHART", "TREATMENT", "FINDING", etc.
  author_id: string;    // Email of creator
  created_at: string;   // ISO8601
  updated_at: string;   // ISO8601
  patient?: PatientSummary; // Only if include_patient=true
}

interface PatientSummary {
  id: string;
  first_name: string;
  last_name: string;
  dob: string;          // YYYY-MM-DD
}
```

---

### GET /api/v1/notes/{note_id}
*Retrieve a single clinical note by ID.*

```
Path Params:
  - note_id (required): UUID

Query Params:
  - include_patient (optional): boolean, default false
  - include_visit (optional): boolean, default false

Response: NoteResponse (with optional patient/visit)

Error Codes:
  - 404: Note not found
  - 403: Note belongs to different office
```

**Example Request:**
```javascript
// Deep link to specific note
const noteId = 'abc123-...';
const response = await fetch(
  `/api/v1/notes/${noteId}?include_patient=true`,
  { headers: { 'Authorization': `Bearer ${token}` }}
);
if (response.status === 404) {
  showError('Note not found');
}
```

---

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

## Changelog

### 2026-02-02 - AI Summary Pipeline Verified

1. **Patient Summary Endpoint Working** - `GET /patients/{id}/summary` returns AI summaries
   - Model: `gpt-4o-mini`
   - Generation: Automatic via Cloud Tasks when notes are created
   - Latency: ~10 seconds for LLM generation

2. **Cloud Tasks Integration Verified** - Note creation triggers async summary generation

### 2026-02-01

1. **Task `assignee_type` field** - Distinguish tasks for dentist vs patient vs front desk
   - Values: `DENTIST` (default), `PATIENT`, `FRONT_DESK`
   - Filter: `GET /tasks?assignee_type=PATIENT`

### 2026-01-30

1. **Added `GET /tasks/{task_id}`** - Was missing, caused 405 on task detail fetch
2. **Corrected `cloudbuild.yaml`** - Fixed `DB_USER=postgres` → `dental_user`
3. **Documented timezone handling** - Created `/docs/TIMEZONE_HANDLING.md`
4. **Verified endpoints locally** - All return 200 OK with valid auth
