# Dental Backend API Reference

**Base URL**: `https://dental-backend-963321342744.us-central1.run.app`

This API enables dental practice management features including patient records, clinical notes (with encryption), task management, and semantic search.

> [!TIP]
> **Interactive Documentation**: Explore and test the API via Swagger UI:
> [**View Swagger Documentation**](https://dental-backend-963321342744.us-central1.run.app/docs)

---

## Authentication

The API supports two methods of authentication.

### 1. Bearer Token (Frontend Users)
Human users authenticate via Email/Password to obtain a JWT.

`Authorization: Bearer <access_token>`

### 2. API Key (System Integrations)
Server-to-server integrations use an API Key.

`X-Office-Key: sk_live_...`

---

## Auth Endpoints

### Login
`POST /api/v1/auth/login`

**Request Body**
| Field | Type | Required |
| :--- | :--- | :--- |
| `email` | string | Yes |
| `password` | string | Yes |

**Response**
```json
{ "access_token": "eyJhbGci...", "token_type": "bearer" }
```

---

### Register (New Office)
`POST /api/v1/auth/register`

Creates a new Office and initial Admin User.

**Request Body**
```json
{
  "office": { "name": "My Practice", "address": "123 Main St" },
  "user": { "email": "admin@example.com", "password": "...", "full_name": "Dr. Smith" }
}
```

**Response**
Returns a Token object.

---

### Create API Key
`POST /api/v1/auth/keys`

Generates a new API key for system integrations. **Requires Bearer Token.**

**Request Body**
| Field | Type | Required |
| :--- | :--- | :--- |
| `name` | string | No |

**Response**
```json
{
  "id": "...",
  "prefix": "sk_live_abc...",
  "name": "Zapier Integration",
  "key": "sk_live_abc123..." // Only returned once!
}
```

---

### List API Keys
`GET /api/v1/auth/keys`

Returns all API keys for the current office. **Requires Bearer Token.**

---

## Patients

### The Patient Object
```json
{
  "id": "3fa85f64-...",
  "first_name": "Jane",
  "last_name": "Doe",
  "dob": "1990-05-15",
  "contact_info": { "email": "...", "phone": "..." },
  "medical_history": { "allergies": ["Penicillin"] },
  "ssn_last_4": "***-**-1234",
  "is_active": true,
  "created_at": "2024-01-28T12:00:00Z"
}
```

### Create a Patient
`POST /api/v1/patients`

| Field | Type | Required |
| :--- | :--- | :--- |
| `first_name` | string | Yes |
| `last_name` | string | Yes |
| `dob` | date | Yes |
| `contact_info` | object | No |
| `medical_history` | object | No |
| `ssn` | string | No |

> [!TIP]
> SSN accepts full format (`123-45-6789`), last 4 digits (`6789`), or omit entirely.

---

### Retrieve a Patient
`GET /api/v1/patients/{id}`

---

### Update a Patient
`PATCH /api/v1/patients/{id}`

| Field | Type | Required |
| :--- | :--- | :--- |
| `first_name` | string | No |
| `last_name` | string | No |
| `dob` | date | No |
| `contact_info` | object | No |
| `medical_history` | object | No |
| `ssn` | string | No |

---

### Delete a Patient
`DELETE /api/v1/patients/{id}`

Soft delete (sets `is_active: false`). Returns `204 No Content`.

---

### Search Patients
`GET /api/v1/patients/search/query`

| Query Param | Type | Required |
| :--- | :--- | :--- |
| `last_name` | string | No (at least one required) |
| `first_name` | string | No |
| `phone` | string | No |

---

### Search by SSN
`GET /api/v1/patients/search/ssn`

Search by full SSN or last 4 digits.

| Query Param | Type | Required |
| :--- | :--- | :--- |
| `ssn` | string | Yes |

---

### Check for Duplicates
`POST /api/v1/patients/check-duplicate`

Check for potential duplicate patients before creation. Returns matches ordered by confidence.

| Field | Type | Required |
| :--- | :--- | :--- |
| `last_name` | string | Yes |
| `dob` | date | Yes |
| `first_name` | string | No |
| `ssn` | string | No |
| `phone` | string | No |

**Response**
```json
{
  "potential_duplicates": [
    {
      "id": "uuid",
      "first_name": "Jane",
      "last_name": "Doe",
      "dob": "1990-05-15",
      "match_confidence": "HIGH",
      "match_reason": "SSN exact match"
    }
  ]
}
```

| Confidence | Criteria |
| :--- | :--- |
| HIGH | Full SSN exact match |
| MEDIUM | SSN last-4 + DOB + Name, or DOB + Full Name |
| LOW | Phone + Name, or DOB + Last Name |

---

## Patient Summaries

AI-generated or manually created patient summaries with version history.

> [!TIP]
> **Auto-Generation**: Summaries are automatically generated via Cloud Tasks when clinical notes are created. The LLM uses the v2 "Pre-Visit Huddle" prompt format.

### How It Works
1. Note created → Cloud Tasks queue triggered
2. LLM generates summary (default: `gpt-4o-mini`, configurable via `LLM_MODEL` env var)
3. Summary saved to `patient_summaries` table with source `"AI"`

### Get Latest Summary
`GET /api/v1/patients/{patient_id}/summary`

Returns the most recent summary for a patient.

**Response:**
```json
{
  "id": "...",
  "patient_id": "...",
  "content": {
    "summary_markdown": "## 60-second snapshot\n- Reason for visit: Routine checkup\n- Key history: Recurring gum issues\n..."
  },
  "source": "AI",
  "model_provider": "openai",
  "model_name": "gpt-4o-mini",
  "prompt_version": "v2",
  "confidence_score": 0.85,
  "created_at": "2026-02-02T10:00:00Z"
}
```

**SummaryContent Schema:**
| Field | Type | Description |
| :--- | :--- | :--- |
| `summary_markdown` | string \| null | **Primary field for AI summaries.** Full markdown narrative. |
| `chief_concerns` | string[] \| null | Legacy/manual: List of concerns |
| `recent_procedures` | string[] \| null | Legacy/manual: Recent procedures |
| `ongoing_treatment` | string \| null | Legacy/manual: Treatment notes |
| `allergies` | string[] \| null | Legacy/manual: Known allergies |
| `medications` | string[] \| null | Legacy/manual: Current medications |
| `notes_summary` | string \| null | Legacy/manual: Notes summary |
| `key_clinical_findings` | string[] \| null | Extracted clinical findings |
| `action_items` | string[] \| null | Follow-up action items |
| `risk_factors` | string[] \| null | Patient risk factors |

> [!IMPORTANT]
> **AI summaries** populate `summary_markdown` with the full narrative. **Manual summaries** use the legacy fields. Frontend should check `content.summary_markdown` first for AI content.

### Get Summary History
`GET /api/v1/patients/{patient_id}/summary/history?limit=20&offset=0`

Returns paginated list of all summaries.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `limit` | int | Max results (default 20, max 100) |
| `offset` | int | Pagination offset |

### Update Summary (Manual Edit)
`PUT /api/v1/patients/{patient_id}/summary`

Manually create or edit a patient summary.

**Request:**
```json
{
  "content": {
    "chief_concerns": ["Edited concern"],
    "ongoing_treatment": "Manual summary by dentist"
  }
}
```

> [!NOTE]
> Manual edits are saved with `source: "MANUAL"` and tracked with `edited_by` user ID.

---

## Visits

### The Visit Object
```json
{
  "id": "...",
  "patient_id": "...",
  "visit_date": "2024-02-01T09:00:00Z",
  "reason": "Routine Checkup",
  "status": "SCHEDULED",
  "duration_minutes": 30
}
```

**Status Values**: `SCHEDULED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `DELETED`

---

### Create a Visit
`POST /api/v1/visits`

| Field | Type | Required |
| :--- | :--- | :--- |
| `patient_id` | UUID | Yes |
| `visit_date` | datetime | Yes |
| `reason` | string | No |
| `status` | string | No |
| `duration_minutes` | int | No |

---

### Get Schedule (Daily View)
`GET /api/v1/visits/schedule`

| Query Param | Type | Required |
| :--- | :--- | :--- |
| `date` | date | Yes |

Returns all visits for the specified date (excludes DELETED).

---

### List Patient Visits
`GET /api/v1/visits/patient/{patient_id}`

---

### Retrieve a Visit
`GET /api/v1/visits/{id}`

---

### Update a Visit
`PATCH /api/v1/visits/{id}`

| Field | Type | Required |
| :--- | :--- | :--- |
| `visit_date` | datetime | No |
| `reason` | string | No |
| `status` | string | No |
| `duration_minutes` | int | No |

---

### Delete a Visit
`DELETE /api/v1/visits/{id}`

Soft delete (sets `status: DELETED`). Returns `204 No Content`.

---

## Clinical Notes

Clinical notes are HIPAA-compliant records attached to patients and optionally to visits. Content is encrypted at rest and automatically decrypted when retrieved.

### The Note Object

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "patient_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "visit_id": "b2c3d4e5-6789-01bc-def0-234567890abc",
  "content": "Patient reports sensitivity to cold on lower right molar.",
  "tooth_number": "14",
  "surface_ids": "MOD",
  "area_of_oral_cavity": "Lower Right",
  "note_type": "CLINICAL",
  "author_id": "dr_smith@example.com",
  "created_at": "2026-01-31T12:00:00Z",
  "updated_at": "2026-01-31T12:00:00Z"
}
```

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Unique identifier for the note. |
| `patient_id` | UUID | ID of the patient this note belongs to. |
| `visit_id` | UUID | Optional. ID of the associated visit. |
| `content` | string | The clinical note content (auto-decrypted). |
| `tooth_number` | string | Optional. Affected tooth (e.g., "14", "32"). |
| `surface_ids` | string | Optional. Tooth surfaces (e.g., "M", "MOD", "BFLI"). |
| `area_of_oral_cavity` | string | Optional. Region (e.g., "Upper Left", "Lower Right"). |
| `note_type` | string | Type of note. Default: `"GENERAL"`. |
| `author_id` | string | Email of the note author. |
| `created_at` | datetime | When the note was created. |
| `updated_at` | datetime | When the note was last updated. |

---

### List All Notes

`GET /api/v1/notes`

Returns a paginated list of clinical notes for the office. Results are sorted by `created_at` descending by default.

#### Query Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `limit` | integer | `50` | Number of notes to return (1-100). |
| `offset` | integer | `0` | Number of notes to skip. |
| `sort` | string | `"created_at"` | Field to sort by (`created_at`, `updated_at`). |
| `order` | string | `"desc"` | Sort order (`asc`, `desc`). |
| `note_type` | string | — | Filter by note type. |
| `patient_id` | UUID | — | Filter by patient. |
| `visit_id` | UUID | — | Filter by visit. |
| `date_from` | datetime | — | Notes created after this date (ISO 8601). |
| `date_to` | datetime | — | Notes created before this date (ISO 8601). |
| `include_patient` | boolean | `false` | Include patient data in each note. |

#### Response

```json
{
  "items": [
    {
      "id": "3fa85f64-...",
      "patient_id": "a1b2c3d4-...",
      "content": "Patient reports sensitivity...",
      "note_type": "CLINICAL",
      "author_id": "dr_smith@example.com",
      "created_at": "2026-01-31T12:00:00Z",
      "updated_at": "2026-01-31T12:00:00Z",
      "patient": null
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

When `include_patient=true`, each note includes embedded patient data:

```json
{
  "items": [
    {
      "id": "3fa85f64-...",
      "content": "...",
      "patient": {
        "id": "a1b2c3d4-...",
        "first_name": "Jane",
        "last_name": "Doe",
        "dob": "1990-05-15T00:00:00"
      }
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

#### Example Request

```bash
curl -X GET "https://dental-backend-963321342744.us-central1.run.app/api/v1/notes?limit=10&include_patient=true" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### Retrieve a Note

`GET /api/v1/notes/{id}`

Retrieves a single clinical note by its unique identifier.

#### Path Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Yes | The note's unique identifier. |

#### Query Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `include_patient` | boolean | `false` | Include patient data in response. |
| `include_visit` | boolean | `false` | Include visit data in response. |

#### Response

Returns a [Note object](#the-note-object). Returns `404` if the note doesn't exist, or `403` if access is denied.

#### Example Request

```bash
curl -X GET "https://dental-backend-963321342744.us-central1.run.app/api/v1/notes/3fa85f64-5717-4562-b3fc-2c963f66afa6?include_patient=true" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### Create a Note

`POST /api/v1/notes`

Creates a new clinical note. **Requires Bearer Token** (author is set from authenticated user).

#### Request Body

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `patient_id` | UUID | Yes | The patient this note belongs to. |
| `content` | string | Yes | The note content. |
| `author_id` | string | Yes | Author email (overwritten by server). |
| `visit_id` | UUID | No | Associated visit ID. |
| `tooth_number` | string | No | Affected tooth number. |
| `surface_ids` | string | No | Tooth surfaces. |
| `note_type` | string | No | Note type. Default: `"GENERAL"`. |
| `area_of_oral_cavity` | string | No | Oral cavity region. |

#### Example Request

```bash
curl -X POST "https://dental-backend-963321342744.us-central1.run.app/api/v1/notes" \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "content": "Patient reports sensitivity to cold.",
    "note_type": "CLINICAL",
    "tooth_number": "14",
    "author_id": "dr_smith@example.com"
  }'
```

---

### Update a Note

`PUT /api/v1/notes/{id}`

Updates an existing clinical note. Creates a history record for audit purposes.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `content` | string | Yes | The updated note content. |
| `author_id` | string | Yes | Author email (for confirmation). |
| `tooth_number` | string | No | Updated tooth number. |
| `surface_ids` | string | No | Updated tooth surfaces. |
| `note_type` | string | No | Updated note type. |

---

### Get Note History

`GET /api/v1/notes/{id}/history`

Returns all previous versions of a clinical note, ordered newest-first. Each update to a note creates a history record containing the previous content. Content is automatically decrypted.

#### Path Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Yes | The note's unique identifier. |

#### Response

```json
{
  "items": [
    {
      "id": "f1e2d3c4-...",
      "previous_content": "Original note text before edit...",
      "edited_by": "dr_smith@example.com",
      "change_reason": "Update",
      "created_at": "2026-01-31T10:00:00Z",
      "tooth_number": "14",
      "surface_ids": "MO",
      "area_of_oral_cavity": "Upper Right",
      "note_type": "CLINICAL"
    }
  ],
  "total": 2
}
```

#### Error Responses

| Code | Description |
| :--- | :--- |
| `404` | Note not found. |
| `403` | Access denied (wrong tenant). |

#### Example Request

```bash
curl -X GET "https://dental-backend-963321342744.us-central1.run.app/api/v1/notes/3fa85f64-5717-4562-b3fc-2c963f66afa6/history" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### List Patient Notes

`GET /api/v1/notes/patient/{patient_id}`

Returns all clinical notes for a specific patient.

#### Path Parameters

| Parameter | Type | Required |
| :--- | :--- | :--- |
| `patient_id` | UUID | Yes |

---

## Bills

### The Bill Object
```json
{
  "id": "...",
  "patient_id": "...",
  "visit_id": "...",
  "amount": 150.00,
  "status": "PENDING",
  "codes": [{ "code": "D0120", "description": "..." }]
}
```

---

### Create a Bill
`POST /api/v1/bills`

| Field | Type | Required |
| :--- | :--- | :--- |
| `patient_id` | UUID | Yes |
| `visit_id` | UUID | Yes |
| `amount` | number | Yes |
| `status` | string | Yes |
| `codes` | list[string] | Yes |

---

### List Patient Bills
`GET /api/v1/bills/patient/{patient_id}`

---

## Tasks

### The Task Object
```json
{
  "id": "...",
  "patient_id": "...",
  "description": "Call patient to reschedule",
  "status": "PENDING",
  "priority": "HIGH",
  "due_date": "2024-02-01",
  "assignee_type": "DENTIST"
}
```

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `assignee_type` | string | Who should perform the task: `DENTIST`, `PATIENT`, `FRONT_DESK`. Default: `DENTIST`. |

---

### Create a Task
`POST /api/v1/tasks`

| Field | Type | Required |
| :--- | :--- | :--- |
| `patient_id` | UUID | Yes |
| `description` | string | Yes |
| `priority` | string | No |
| `status` | string | No |
| `due_date` | date | No |
| `generated_by` | string | No |
| `assignee_type` | string | No |

---

### List Patient Tasks
`GET /api/v1/tasks/patient/{patient_id}`

---

### Update a Task
`PATCH /api/v1/tasks/{id}`

| Field | Type | Required |
| :--- | :--- | :--- |
| `description` | string | No |
| `status` | string | No |
| `priority` | string | No |
| `due_date` | date | No |
| `assignee_type` | string | No |

---

### Delete a Task
`DELETE /api/v1/tasks/{id}`

Hard delete. Returns `204 No Content`.

---

## Quick Phrases

### The Quick Phrase Object
```json
{
  "id": "...",
  "text": "Patient setup and draped.",
  "category": "Pre-op",
  "usage_count": 42
}
```

---

### Create a Phrase
`POST /api/v1/quick_phrases`

| Field | Type | Required |
| :--- | :--- | :--- |
| `text` | string | Yes |
| `category` | string | No |

---

### List Phrases
`GET /api/v1/quick_phrases`

| Query Param | Type | Required |
| :--- | :--- | :--- |
| `category` | string | No |

---

### Update a Phrase
`PUT /api/v1/quick_phrases/{id}`

| Field | Type | Required |
| :--- | :--- | :--- |
| `text` | string | No |
| `category` | string | No |
| `usage_count` | integer | No |

---

### Delete a Phrase
`DELETE /api/v1/quick_phrases/{id}`

Hard delete. Returns `204 No Content`.

---

## Search

### Search Notes
`POST /api/v1/search`

Semantic + keyword search across all clinical notes.

| Field | Type | Required |
| :--- | :--- | :--- |
| `query` | string | Yes |
| `limit` | integer | No |

**Response**: List of [Note](#the-note-object) objects.

---

## Backfill (Historical Data Import)

Endpoints for importing historical data with custom `created_at` timestamps.

> [!IMPORTANT]
> **API Key Required**: All backfill endpoints require `X-Office-Key` header authentication. Bearer tokens are rejected.

### Common Request Fields

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `created_at` | datetime | Yes | Must be in the past (ISO 8601). |

### Backfill a Patient
`POST /api/v1/backfill/patients`

Creates a patient with custom `created_at`. Sets `is_backfilled: true`.

| Field | Type | Required |
| :--- | :--- | :--- |
| `first_name` | string | Yes |
| `last_name` | string | Yes |
| `dob` | date | Yes |
| `created_at` | datetime | Yes |
| `contact_info` | object | No |
| `medical_history` | object | No |

---

### Backfill a Visit
`POST /api/v1/backfill/visits`

Creates a visit with custom `created_at`. Sets `is_backfilled: true`.

| Field | Type | Required |
| :--- | :--- | :--- |
| `patient_id` | UUID | Yes |
| `visit_date` | datetime | Yes |
| `created_at` | datetime | Yes |
| `reason` | string | No |
| `status` | string | No |

---

### Backfill a Note
`POST /api/v1/backfill/notes`

Creates a clinical note with custom `created_at`. Sets `is_backfilled: true`.

| Field | Type | Required |
| :--- | :--- | :--- |
| `patient_id` | UUID | Yes |
| `content` | string | Yes |
| `author_id` | string | Yes |
| `created_at` | datetime | Yes |
| `visit_id` | UUID | No |
| `tooth_number` | string | No |
| `surface_ids` | string | No |
| `note_type` | string | No |

---

### Backfill a Bill
`POST /api/v1/backfill/bills`

Creates a bill with custom `created_at`. Sets `is_backfilled: true`.

| Field | Type | Required |
| :--- | :--- | :--- |
| `patient_id` | UUID | Yes |
| `visit_id` | UUID | Yes |
| `amount` | number | Yes |
| `status` | string | Yes |
| `codes` | list[string] | Yes |
| `created_at` | datetime | Yes |

---

### Response Format

All backfill endpoints return:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "created_at": "2023-06-15T10:30:00Z",
  "is_backfilled": true
}
```

---

## Errors

| Code | Meaning |
| :--- | :--- |
| `200` | OK |
| `204` | No Content (successful delete) |
| `400` | Bad Request |
| `401` | Unauthorized |
| `404` | Not Found |
| `422` | Validation Error |
| `500` | Server Error |
