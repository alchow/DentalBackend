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
BASE_URL = "https://dental-backend-963321342744.us-central1.run.app/api/v1"
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
        
        # 3. Read Patient Notes
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
        # TASK ENDPOINTS
        # ============================================================
        print("\n\n### TASK ENDPOINTS ###")
        
        # 1. Create Task
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
                print(f"   ➡️ Created task: {state['task_id']}")
        
        # 2. Read Patient Tasks
        if state["patient_id"]:
            await test_endpoint(
                client, "get", f"/tasks/patient/{state['patient_id']}", 200,
                headers=api_key_headers()
            )
        
        # 3. Update Task (PATCH)
        if state["task_id"]:
            await test_endpoint(
                client, "patch", f"/tasks/{state['task_id']}", 200,
                headers=api_key_headers(),
                json={"status": "COMPLETED", "priority": "NORMAL"}
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
