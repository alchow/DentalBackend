#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Dental Backend (Production GCP)

This script tests all API endpoints against the production deployment.
It creates real data in the production database as confirmed by the user.

Usage:
    python test_all_apis.py

Known Issues:
    - Visit GET/PATCH/DELETE endpoints return 500 due to missing 'DELETED' value
      in PostgreSQL visitstatus enum. Migration needs to be applied:
      ALTER TYPE visitstatus ADD VALUE 'DELETED';
"""

import httpx
import asyncio
from datetime import date, datetime, timedelta
import uuid
import json

# Configuration
BASE_URL = "https://dental-backend-2iw4ademaa-uc.a.run.app/api/v1"
TEST_EMAIL = f"test-{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "TestPassword123!"

# Global state to track created resources
state = {
    "access_token": None,
    "office_id": None,
    "patient_id": None,
    "visit_id": None,
    "note_id": None,
    "bill_id": None,
    "task_id": None,
    "quick_phrase_id": None,
    "api_key": None,
}


def auth_headers():
    """Return headers with Bearer token."""
    return {"Authorization": f"Bearer {state['access_token']}"}


def api_key_headers():
    """Return headers with both Bearer token and X-Office-Key for maximum compatibility."""
    headers = {}
    if state["access_token"]:
        headers["Authorization"] = f"Bearer {state['access_token']}"
    if state["api_key"]:
        headers["X-Office-Key"] = state["api_key"]
    return headers if headers else auth_headers()


async def test_endpoint(client, method, path, expected_status, **kwargs):
    """Helper to test an endpoint and print results."""
    url = f"{BASE_URL}{path}"
    print(f"\n{'='*60}")
    print(f"TEST: {method.upper()} {path}")
    
    try:
        response = await getattr(client, method)(url, **kwargs)
        status_ok = response.status_code == expected_status
        status_icon = "✅" if status_ok else "❌"
        
        print(f"{status_icon} Status: {response.status_code} (expected {expected_status})")
        
        if response.status_code < 400:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, default=str)[:200]}...")
                return data
            except:
                print(f"   Response: {response.text[:200]}...")
                return response.text
        else:
            print(f"   Error: {response.text[:300]}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


async def main():
    print("="*60)
    print("DENTAL BACKEND API TEST SUITE")
    print(f"Target: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # ============================================================
        # AUTH ENDPOINTS
        # ============================================================
        print("\n\n### AUTH ENDPOINTS ###")
        
        # 1. Register
        data = await test_endpoint(
            client, "post", "/auth/register", 200,
            json={
                "office": {"name": "API Test Office", "address": "123 Test St"},
                "user": {"email": TEST_EMAIL, "password": TEST_PASSWORD, "full_name": "API Test User"}
            }
        )
        if data:
            state["access_token"] = data.get("access_token")
            print(f"   ➡️ Got access token: {state['access_token'][:20]}...")
        
        # 2. Login
        data = await test_endpoint(
            client, "post", "/auth/login", 200,
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if data:
            state["access_token"] = data.get("access_token")
        
        # 3. Create API Key
        data = await test_endpoint(
            client, "post", "/auth/keys", 200,
            headers=auth_headers(),
            json={"name": "Test API Key"}
        )
        if data:
            state["api_key"] = data.get("key")
            print(f"   ➡️ Got API key: {state['api_key'][:20]}...")
        
        # 4. List API Keys
        await test_endpoint(
            client, "get", "/auth/keys", 200,
            headers=auth_headers()
        )
        
        # ============================================================
        # PATIENT ENDPOINTS
        # ============================================================
        print("\n\n### PATIENT ENDPOINTS ###")
        
        # 1. Create Patient
        data = await test_endpoint(
            client, "post", "/patients", 200,
            headers=api_key_headers(),
            json={
                "first_name": "John",
                "last_name": "Doe",
                "dob": "1990-05-15",
                "contact_info": {"phone": "555-1234", "email": "john.doe@test.com"},
                "medical_history": {"allergies": ["None known"], "medications": []}
            }
        )
        if data:
            state["patient_id"] = data.get("id")
            print(f"   ➡️ Created patient: {state['patient_id']}")
        
        # 2. Read Patient
        if state["patient_id"]:
            await test_endpoint(
                client, "get", f"/patients/{state['patient_id']}", 200,
                headers=api_key_headers()
            )
        
        # 3. Update Patient (PATCH)
        if state["patient_id"]:
            await test_endpoint(
                client, "patch", f"/patients/{state['patient_id']}", 200,
                headers=api_key_headers(),
                json={"medical_history": {"allergies": ["None known"], "medications": [], "notes": "Tested negative for latex"}}
            )
        
        # 4. Search Patients
        await test_endpoint(
            client, "get", "/patients/search/query?last_name=Doe", 200,
            headers=api_key_headers()
        )
        
        # 5. Create Patient with SSN (full)
        ssn_patient_data = await test_endpoint(
            client, "post", "/patients", 200,
            headers=api_key_headers(),
            json={
                "first_name": "Sarah",
                "last_name": "Smith",
                "dob": "1985-03-20",
                "ssn": "123-45-6789",  # Full SSN
                "contact_info": {"phone": "555-9999"}
            }
        )
        ssn_patient_id = None
        if ssn_patient_data:
            ssn_patient_id = ssn_patient_data.get("id")
            ssn_last_4 = ssn_patient_data.get("ssn_last_4")
            print(f"   ➡️ Created SSN patient: {ssn_patient_id}")
            print(f"   ➡️ SSN masked: {ssn_last_4}")
        
        # 6. Search by SSN (full)
        if ssn_patient_id:
            await test_endpoint(
                client, "get", "/patients/search/ssn?ssn=123-45-6789", 200,
                headers=api_key_headers()
            )
        
        # 7. Search by SSN (last 4)
        if ssn_patient_id:
            await test_endpoint(
                client, "get", "/patients/search/ssn?ssn=6789", 200,
                headers=api_key_headers()
            )
        
        # 8. Check Duplicate - should find HIGH confidence match
        if ssn_patient_id:
            dup_response = await test_endpoint(
                client, "post", "/patients/check-duplicate", 200,
                headers=api_key_headers(),
                json={
                    "first_name": "Sarah",
                    "last_name": "Smith",
                    "dob": "1985-03-20",
                    "ssn": "123-45-6789"  # Same SSN
                }
            )
            if dup_response and dup_response.get("potential_duplicates"):
                first_match = dup_response["potential_duplicates"][0]
                print(f"   ➡️ Duplicate found: {first_match.get('match_confidence')} - {first_match.get('match_reason')}")
        
        # 9. Check Duplicate - no match expected
        await test_endpoint(
            client, "post", "/patients/check-duplicate", 200,
            headers=api_key_headers(),
            json={
                "first_name": "Unique",
                "last_name": "Person",
                "dob": "1999-12-31"
            }
        )
        
        # ============================================================
        # VISIT ENDPOINTS
        # ============================================================
        print("\n\n### VISIT ENDPOINTS ###")
        
        # 1. Create Visit
        if state["patient_id"]:
            data = await test_endpoint(
                client, "post", "/visits", 200,
                headers=api_key_headers(),
                json={
                    "patient_id": state["patient_id"],
                    "visit_date": datetime.now().isoformat(),
                    "reason": "Routine checkup",
                    "status": "SCHEDULED"
                }
            )
            if data:
                state["visit_id"] = data.get("id")
                print(f"   ➡️ Created visit: {state['visit_id']}")
        
        # 2. Get Schedule (today)
        today = date.today().isoformat()
        await test_endpoint(
            client, "get", f"/visits/schedule?date={today}", 200,
            headers=api_key_headers()
        )
        
        # 3. Read Patient Visits
        if state["patient_id"]:
            await test_endpoint(
                client, "get", f"/visits/patient/{state['patient_id']}", 200,
                headers=api_key_headers()
            )
        
        # 4. Read Single Visit
        if state["visit_id"]:
            await test_endpoint(
                client, "get", f"/visits/{state['visit_id']}", 200,
                headers=api_key_headers()
            )
        
        # 5. Update Visit (PATCH)
        if state["visit_id"]:
            await test_endpoint(
                client, "patch", f"/visits/{state['visit_id']}", 200,
                headers=api_key_headers(),
                json={"status": "IN_PROGRESS", "reason": "Routine checkup - in progress"}
            )
        
        # ============================================================
        # NOTE ENDPOINTS
        # ============================================================
        print("\n\n### NOTE ENDPOINTS ###")
        
        # 1. Create Note
        if state["patient_id"] and state["visit_id"]:
            data = await test_endpoint(
                client, "post", "/notes", 200,
                headers=auth_headers(),  # Notes require user auth for author tracking
                json={
                    "patient_id": state["patient_id"],
                    "visit_id": state["visit_id"],
                    "content": "Patient presented with mild gum inflammation. Recommended improved flossing technique.",
                    "note_type": "clinical",
                    "area_of_oral_cavity": "Upper Right",
                    "tooth_number": "14",
                    "surface_ids": "M,O",  # String, not array
                    "author_id": TEST_EMAIL  # Required by schema
                }
            )
            if data:
                state["note_id"] = data.get("id")
                print(f"   ➡️ Created note: {state['note_id']}")
        
        # 2. Update Note
        if state["note_id"]:
            await test_endpoint(
                client, "put", f"/notes/{state['note_id']}", 200,
                headers=auth_headers(),
                json={
                    "content": "UPDATED: Patient presented with mild gum inflammation. Prescribed chlorhexidine rinse.",
                    "note_type": "clinical",
                    "area_of_oral_cavity": "Upper Right",
                    "tooth_number": "14",
                    "surface_ids": "M,O,D",  # String, not array
                    "author_id": TEST_EMAIL  # Required  
                }
            )
        
        # 3. Get Note History (tests version control)
        if state["note_id"]:
            data = await test_endpoint(
                client, "get", f"/notes/{state['note_id']}/history", 200,
                headers=auth_headers()
            )
            if data and data.get("total", 0) > 0:
                print(f"   ➡️ Found {data['total']} history entries")
        
        # 4. Read Patient Notes
        if state["patient_id"]:
            await test_endpoint(
                client, "get", f"/notes/patient/{state['patient_id']}", 200,
                headers=api_key_headers()
            )
        
        # ============================================================
        # BILL ENDPOINTS
        # ============================================================
        print("\n\n### BILL ENDPOINTS ###")
        
        # 1. Create Bill
        if state["patient_id"] and state["visit_id"]:
            data = await test_endpoint(
                client, "post", "/bills", 200,
                headers=api_key_headers(),
                json={
                    "patient_id": state["patient_id"],
                    "visit_id": state["visit_id"],
                    "amount": 150.00,
                    "status": "PENDING",
                    "codes": ["D0120", "D1110"]
                }
            )
            if data:
                state["bill_id"] = data.get("id")
                print(f"   ➡️ Created bill: {state['bill_id']}")
        
        # 2. Read Patient Bills
        if state["patient_id"]:
            await test_endpoint(
                client, "get", f"/bills/patient/{state['patient_id']}", 200,
                headers=api_key_headers()
            )
        
        # ============================================================
        # PATIENT SUMMARY ENDPOINTS
        # ============================================================
        print("\n\n### PATIENT SUMMARY ENDPOINTS ###")
        
        # 1. Get Latest Summary (expect 404 - no summary yet)
        if state["patient_id"]:
            await test_endpoint(
                client, "get", f"/patients/{state['patient_id']}/summary", 404,
                headers=api_key_headers()
            )
            print("   ➡️ No summary yet (expected)")
        
        # 2. Create Manual Summary
        if state["patient_id"]:
            data = await test_endpoint(
                client, "put", f"/patients/{state['patient_id']}/summary", 200,
                headers=auth_headers(),
                json={
                    "content": {
                        "chief_concerns": ["Test concern"],
                        "ongoing_treatment": "E2E test manual summary",
                        "allergies": ["Penicillin"]
                    }
                }
            )
            if data:
                summary_id = data.get("id")
                source = data.get("source")
                print(f"   ➡️ Created summary: {summary_id}")
                print(f"   ➡️ Source: {source}")
        
        # 3. Get Latest Summary (should now exist)
        if state["patient_id"]:
            data = await test_endpoint(
                client, "get", f"/patients/{state['patient_id']}/summary", 200,
                headers=api_key_headers()
            )
            if data:
                content = data.get("content", {})
                print(f"   ➡️ Content has {len(content)} fields")
        
        # 4. Update Summary (create v2)
        if state["patient_id"]:
            data = await test_endpoint(
                client, "put", f"/patients/{state['patient_id']}/summary", 200,
                headers=auth_headers(),
                json={
                    "content": {
                        "chief_concerns": ["Updated concern"],
                        "ongoing_treatment": "Updated by E2E test",
                        "allergies": ["Penicillin", "Latex"]
                    }
                }
            )
            if data:
                print(f"   ➡️ Updated summary (v2)")
        
        # 5. Get Summary History (should have 2 entries)
        if state["patient_id"]:
            data = await test_endpoint(
                client, "get", f"/patients/{state['patient_id']}/summary/history?limit=10&offset=0", 200,
                headers=api_key_headers()
            )
            if data:
                total = data.get("total", 0)
                items = data.get("items", [])
                print(f"   ➡️ History: {total} summaries, returned {len(items)}")
        
        # ============================================================
        # AI-GENERATED SUMMARY TEST (Note → Summary Pipeline)
        # ============================================================
        print("\n\n### AI-GENERATED SUMMARY TEST ###")
        print("   Testing: Create note → Verify AI summary generated")
        
        # Create a new patient for AI summary test (to avoid manual summary interference)
        ai_test_patient_id = None
        ai_test_visit_id = None
        
        # 1. Create dedicated AI test patient
        data = await test_endpoint(
            client, "post", "/patients", 200,
            headers=api_key_headers(),
            json={
                "first_name": "AITest",
                "last_name": "Patient",
                "dob": "1988-07-20",
                "contact_info": {"phone": "555-AI00"}
            }
        )
        if data:
            ai_test_patient_id = data.get("id")
            print(f"   ➡️ Created AI test patient: {ai_test_patient_id}")
        
        # 2. Create visit for AI test patient
        if ai_test_patient_id:
            data = await test_endpoint(
                client, "post", "/visits", 200,
                headers=api_key_headers(),
                json={
                    "patient_id": ai_test_patient_id,
                    "visit_date": datetime.now().isoformat(),
                    "reason": "AI summary test visit",
                    "status": "SCHEDULED"
                }
            )
            if data:
                ai_test_visit_id = data.get("id")
        
        # 3. Verify no summary exists yet
        if ai_test_patient_id:
            await test_endpoint(
                client, "get", f"/patients/{ai_test_patient_id}/summary", 404,
                headers=api_key_headers()
            )
            print("   ➡️ Confirmed no AI summary yet (expected)")
        
        # 4. Create clinical note (triggers summary generation)
        import time
        if ai_test_patient_id and ai_test_visit_id:
            clinical_note = """
            Chief Complaint: Upper right molar sensitivity.
            History: Started 2 weeks ago, worse with cold.
            Findings: Tooth #14 shows distal caries, mild percussion sensitivity.
            Assessment: Reversible pulpitis.
            Plan: Excavate and restore with composite. Review in 2 weeks.
            """
            
            start_time = time.time()
            data = await test_endpoint(
                client, "post", "/notes", 200,
                headers=auth_headers(),
                json={
                    "patient_id": ai_test_patient_id,
                    "visit_id": ai_test_visit_id,
                    "content": clinical_note,
                    "note_type": "clinical",
                    "area_of_oral_cavity": "Upper Right",
                    "tooth_number": "14",
                    "surface_ids": "O,D",
                    "author_id": TEST_EMAIL  # Required field
                }
            )
            elapsed = time.time() - start_time
            if data:
                print(f"   ➡️ Created note (took {elapsed:.2f}s, includes sync summary if enabled)")
        
        # 5. Poll for AI-generated summary (sync mode: immediate, async: poll)
        # Note: LLM generation takes ~8-10s, plus Cloud Tasks delivery time
        ai_summary_found = False
        if ai_test_patient_id:
            max_retries = 15  # 15 * 2s = 30s max wait
            retry_delay = 2
            
            for attempt in range(max_retries):
                response = await client.get(
                    f"{BASE_URL}/patients/{ai_test_patient_id}/summary",
                    headers=api_key_headers()
                )
                
                if response.status_code == 200:
                    ai_summary_found = True
                    summary_data = response.json()
                    source = summary_data.get("source")
                    model = summary_data.get("model_name")
                    print(f"   ✅ AI SUMMARY GENERATED!")
                    print(f"   ├── Source: {source}")
                    print(f"   ├── Model: {model}")
                    content = summary_data.get("content", {})
                    if content.get("summary_markdown"):
                        preview = content["summary_markdown"][:100].replace("\n", " ")
                        print(f"   └── Preview: {preview}...")
                    break
                elif response.status_code == 404 and attempt < max_retries - 1:
                    print(f"   ⏳ Attempt {attempt + 1}/{max_retries}: Waiting for summary...")
                    import asyncio
                    await asyncio.sleep(retry_delay)
            
            if not ai_summary_found:
                print("   ❌ AI SUMMARY NOT GENERATED (check SUMMARY_SYNC_MODE or Cloud Tasks)")
        
        
        # ============================================================
        # TASK ENDPOINTS
        # ============================================================
        print("\n\n### TASK ENDPOINTS ###")
        
        # 1. Create Task (with assignee_type = DENTIST default)
        if state["patient_id"]:
            data = await test_endpoint(
                client, "post", "/tasks", 200,
                headers=api_key_headers(),
                json={
                    "patient_id": state["patient_id"],
                    "description": "Follow up on gum inflammation in 2 weeks",
                    "status": "PENDING",
                    "priority": "HIGH",
                    "due_date": (date.today() + timedelta(days=14)).isoformat(),
                    "generated_by": "API Test"
                }
            )
            if data:
                state["task_id"] = data.get("id")
                assignee_type = data.get("assignee_type", "NOT_RETURNED")
                print(f"   ➡️ Created task: {state['task_id']}")
                print(f"   ➡️ Default assignee_type: {assignee_type}")
        
        # 2. Create Task with explicit PATIENT assignee_type
        patient_task_id = None
        if state["patient_id"]:
            data = await test_endpoint(
                client, "post", "/tasks", 200,
                headers=api_key_headers(),
                json={
                    "patient_id": state["patient_id"],
                    "description": "Floss daily and use prescribed mouthwash",
                    "status": "PENDING",
                    "priority": "NORMAL",
                    "assignee_type": "PATIENT"
                }
            )
            if data:
                patient_task_id = data.get("id")
                assignee_type = data.get("assignee_type", "NOT_RETURNED")
                print(f"   ➡️ Created PATIENT task: {patient_task_id}")
                print(f"   ➡️ assignee_type: {assignee_type}")
        
        # 3. List Tasks filtered by assignee_type
        await test_endpoint(
            client, "get", "/tasks?assignee_type=PATIENT", 200,
            headers=api_key_headers()
        )
        
        await test_endpoint(
            client, "get", "/tasks?assignee_type=DENTIST", 200,
            headers=api_key_headers()
        )
        
        # 4. Read Patient Tasks
        if state["patient_id"]:
            await test_endpoint(
                client, "get", f"/tasks/patient/{state['patient_id']}", 200,
                headers=api_key_headers()
            )
        
        # 5. Update Task (PATCH) - change assignee_type to FRONT_DESK
        if state["task_id"]:
            data = await test_endpoint(
                client, "patch", f"/tasks/{state['task_id']}", 200,
                headers=api_key_headers(),
                json={"status": "COMPLETED", "priority": "NORMAL", "assignee_type": "FRONT_DESK"}
            )
            if data:
                updated_assignee = data.get("assignee_type", "NOT_RETURNED")
                print(f"   ➡️ Updated assignee_type to: {updated_assignee}")
        
        # 6. Delete patient task (cleanup)
        if patient_task_id:
            await test_endpoint(
                client, "delete", f"/tasks/{patient_task_id}", 204,
                headers=api_key_headers()
            )
        
        # ============================================================
        # QUICK PHRASE ENDPOINTS
        # ============================================================
        print("\n\n### QUICK PHRASE ENDPOINTS ###")
        
        # 1. Create Quick Phrase
        data = await test_endpoint(
            client, "post", "/quick_phrases", 200,
            headers=api_key_headers(),
            json={
                "text": "Patient tolerated procedure well.",
                "category": "clinical"
            }
        )
        if data:
            state["quick_phrase_id"] = data.get("id")
            print(f"   ➡️ Created quick phrase: {state['quick_phrase_id']}")
        
        # 2. List Quick Phrases
        await test_endpoint(
            client, "get", "/quick_phrases", 200,
            headers=api_key_headers()
        )
        
        # 3. List Quick Phrases (filtered by category)
        await test_endpoint(
            client, "get", "/quick_phrases?category=clinical", 200,
            headers=api_key_headers()
        )
        
        # 4. Update Quick Phrase
        if state["quick_phrase_id"]:
            await test_endpoint(
                client, "put", f"/quick_phrases/{state['quick_phrase_id']}", 200,
                headers=api_key_headers(),
                json={"text": "Patient tolerated procedure well. No complications.", "category": "clinical"}
            )
        
        # ============================================================
        # SEARCH ENDPOINTS
        # ============================================================
        print("\n\n### SEARCH ENDPOINTS ###")
        
        # 1. Search Notes
        await test_endpoint(
            client, "post", "/search", 200,
            headers=api_key_headers(),
            json={"query": "gum inflammation", "limit": 5}
        )
        
        # ============================================================
        # BACKFILL ENDPOINTS (API Key Only)
        # ============================================================
        print("\n\n### BACKFILL ENDPOINTS ###")
        
        # Test backfill requires API key (Bearer token alone should fail)
        print("\n--- Testing API-key-only requirement ---")
        await test_endpoint(
            client, "post", "/backfill/notes", 401,
            headers=auth_headers(),  # Only Bearer token, no API key
            json={
                "patient_id": state["patient_id"],
                "content": "Backfill test note",
                "author_id": TEST_EMAIL,
                "created_at": "2023-06-15T10:30:00Z"
            }
        )
        
        # 1. Backfill Patient (with past date)
        backfill_patient_data = await test_endpoint(
            client, "post", "/backfill/patients", 201,
            headers={"X-Office-Key": state["api_key"]},  # API key only
            json={
                "first_name": "Historical",
                "last_name": "Patient",
                "dob": "1985-03-20",
                "created_at": "2020-01-15T09:00:00Z"
            }
        )
        if backfill_patient_data:
            print(f"   ➡️ Backfilled patient: {backfill_patient_data.get('id')}")
            print(f"   ➡️ is_backfilled: {backfill_patient_data.get('is_backfilled')}")
            state["backfill_patient_id"] = backfill_patient_data.get("id")
        
        # 2. Backfill Visit (with past date)
        if state.get("backfill_patient_id"):
            backfill_visit_data = await test_endpoint(
                client, "post", "/backfill/visits", 201,
                headers={"X-Office-Key": state["api_key"]},
                json={
                    "patient_id": state["backfill_patient_id"],
                    "visit_date": "2020-01-15T10:00:00Z",
                    "reason": "Historical checkup",
                    "status": "COMPLETED",
                    "created_at": "2020-01-15T10:00:00Z"
                }
            )
            if backfill_visit_data:
                print(f"   ➡️ Backfilled visit: {backfill_visit_data.get('id')}")
                state["backfill_visit_id"] = backfill_visit_data.get("id")
        
        # 3. Backfill Note (with past date)
        if state.get("backfill_patient_id") and state.get("backfill_visit_id"):
            backfill_note_data = await test_endpoint(
                client, "post", "/backfill/notes", 201,
                headers={"X-Office-Key": state["api_key"]},
                json={
                    "patient_id": state["backfill_patient_id"],
                    "visit_id": state["backfill_visit_id"],
                    "content": "Historical note from 2020 checkup.",
                    "author_id": TEST_EMAIL,
                    "note_type": "CLINICAL",
                    "created_at": "2020-01-15T10:30:00Z"
                }
            )
            if backfill_note_data:
                print(f"   ➡️ Backfilled note: {backfill_note_data.get('id')}")
        
        # 4. Backfill Bill (with past date)
        if state.get("backfill_patient_id") and state.get("backfill_visit_id"):
            backfill_bill_data = await test_endpoint(
                client, "post", "/backfill/bills", 201,
                headers={"X-Office-Key": state["api_key"]},
                json={
                    "patient_id": state["backfill_patient_id"],
                    "visit_id": state["backfill_visit_id"],
                    "amount": 75.00,
                    "status": "PAID",
                    "codes": ["D0120"],
                    "created_at": "2020-01-15T11:00:00Z"
                }
            )
            if backfill_bill_data:
                print(f"   ➡️ Backfilled bill: {backfill_bill_data.get('id')}")
        
        # 5. Test future date validation (should fail)
        print("\n--- Testing future date validation ---")
        await test_endpoint(
            client, "post", "/backfill/notes", 422,
            headers={"X-Office-Key": state["api_key"]},
            json={
                "patient_id": state["patient_id"],
                "content": "This should fail - future date",
                "author_id": TEST_EMAIL,
                "created_at": "2030-01-15T10:30:00Z"  # Future date
            }
        )
        
        # ============================================================
        # CLEANUP / DELETE OPERATIONS
        # ============================================================
        print("\n\n### CLEANUP (DELETE OPERATIONS) ###")
        
        # Delete Quick Phrase
        if state["quick_phrase_id"]:
            await test_endpoint(
                client, "delete", f"/quick_phrases/{state['quick_phrase_id']}", 204,
                headers=api_key_headers()
            )
        
        # Delete Task
        if state["task_id"]:
            await test_endpoint(
                client, "delete", f"/tasks/{state['task_id']}", 204,
                headers=api_key_headers()
            )
        
        # Delete Visit (soft delete)
        if state["visit_id"]:
            await test_endpoint(
                client, "delete", f"/visits/{state['visit_id']}", 204,
                headers=api_key_headers()
            )
        
        # Delete Patient (soft delete)
        if state["patient_id"]:
            await test_endpoint(
                client, "delete", f"/patients/{state['patient_id']}", 204,
                headers=api_key_headers()
            )
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n\n" + "="*60)
        print("TEST SUITE COMPLETE")
        print("="*60)
        print(f"""
Resources Created (for reference):
  - User Email: {TEST_EMAIL}
  - Patient ID: {state['patient_id']}
  - Visit ID:   {state['visit_id']}
  - Note ID:    {state['note_id']}
  - Bill ID:    {state['bill_id']}
  - Task ID:    {state['task_id']} (deleted)
  - Phrase ID:  {state['quick_phrase_id']} (deleted)
  - API Key:    {state['api_key'][:20] if state['api_key'] else 'N/A'}...
""")


if __name__ == "__main__":
    asyncio.run(main())
