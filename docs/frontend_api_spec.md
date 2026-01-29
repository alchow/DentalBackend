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

---

### Delete a Patient
`DELETE /api/v1/patients/{id}`

Soft delete (sets `is_active: false`). Returns `204 No Content`.

---

### Search Patients
`GET /api/v1/patients/search/query`

| Query Param | Type | Required |
| :--- | :--- | :--- |
| `last_name` | string | Yes |

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
  "summary": {}
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
| `summary` | object | No |

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
| `summary` | object | No |

---

### Delete a Visit
`DELETE /api/v1/visits/{id}`

Soft delete (sets `status: DELETED`). Returns `204 No Content`.

---

## Clinical Notes

### The Note Object
```json
{
  "id": "...",
  "patient_id": "...",
  "visit_id": "...",
  "content": "Patient reports sensitivity...",
  "tooth_number": "14",
  "surface_ids": "MOD",
  "note_type": "EMERGENCY",
  "author_id": "dr_smith@example.com"
}
```

---

### Create a Note
`POST /api/v1/notes`

| Field | Type | Required |
| :--- | :--- | :--- |
| `patient_id` | UUID | Yes |
| `content` | string | Yes |
| `author_id` | string | Yes* |
| `visit_id` | UUID | No |
| `tooth_number` | string | No |
| `surface_ids` | string | No |
| `note_type` | string | No |
| `area_of_oral_cavity` | string | No |

*`author_id` is overwritten by Backend with logged-in user's email.

---

### Update a Note
`PUT /api/v1/notes/{id}`

| Field | Type | Required |
| :--- | :--- | :--- |
| `content` | string | Yes |
| `author_id` | string | Yes |
| `tooth_number` | string | No |
| `surface_ids` | string | No |
| `note_type` | string | No |

---

### List Patient Notes
`GET /api/v1/notes/patient/{patient_id}`

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
  "due_date": "2024-02-01"
}
```

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
