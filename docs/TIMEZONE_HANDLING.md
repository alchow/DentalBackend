# API Timezone Handling

> **For Frontend Developers**: How to handle dates and times when interacting with the Dental Backend API.

---

## Core Principle

**All timestamps in the API are in UTC.** The frontend is responsible for converting to/from the user's local timezone.

---

## DateTime Fields

| Field | Format | Timezone |
|-------|--------|----------|
| `created_at` | ISO 8601 | UTC (`2026-01-29T15:30:00Z`) |
| `updated_at` | ISO 8601 | UTC |
| `visit_date` | ISO 8601 | UTC |
| `archived_at` | ISO 8601 | UTC |

---

## Schedule Endpoint

### `GET /api/v1/visits/schedule?date=YYYY-MM-DD`

**Current Behavior:**
- The `date` parameter is interpreted as a **UTC date**
- Returns visits where `visit_date` falls on that UTC calendar day

**Frontend Responsibility:**
To show visits for "January 29th" in PST (UTC-8):
1. Calculate UTC range: `2026-01-29T08:00:00Z` to `2026-01-30T07:59:59Z`
2. Query with: `?date=2026-01-29` (primary day) AND `?date=2026-01-30` (for late-night visits)
3. Filter client-side to show only local January 29th

**Example (PST Office):**
```javascript
// User wants to see schedule for Jan 29, 2026 (PST)
const localDate = new Date('2026-01-29');
const utcDate = localDate.toISOString().split('T')[0]; // "2026-01-29"

// Note: Late evening appointments (after 4pm PST) roll into next UTC day
// Frontend should fetch both days and filter
```

---

## Creating Visits

### `POST /api/v1/visits`

**Send timestamps in UTC:**
```json
{
  "patient_id": "uuid",
  "visit_date": "2026-01-29T17:00:00Z",  // 9 AM PST = 5 PM UTC
  "reason": "Cleaning"
}
```

**Frontend Conversion:**
```javascript
// User selects 9:00 AM local time
const localTime = new Date('2026-01-29T09:00:00');
const utcTime = localTime.toISOString();  // "2026-01-29T17:00:00.000Z"
```

---

## Future: Office Timezone Field

If multi-timezone support becomes complex, we may add:
```json
{
  "office": {
    "timezone": "America/Los_Angeles"
  }
}
```

This would allow the backend to handle timezone conversion. For V1, frontend owns this.

---

## Quick Reference

| Operation | Frontend Action |
|-----------|-----------------|
| Display timestamp | Convert UTC → local |
| Submit timestamp | Convert local → UTC |
| Query by date | Send UTC date, filter results locally |
| Store user preference | Track office timezone in frontend state |
