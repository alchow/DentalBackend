#!/usr/bin/env python3
"""
QA Test: Note Summary Pipeline

This test specifically validates the end-to-end flow:
1. Create a patient
2. Create a visit  
3. Create a note
4. Verify summary was generated (sync mode) or poll for it (async mode)

Run: SUMMARY_SYNC_MODE=true python tests/e2e/test_summary_pipeline.py

Requirements:
- Local backend running on 127.0.0.1:8000
- Cloud SQL Proxy running on port 5432 (or 5433)
- .env with SUMMARY_SYNC_MODE=true for local testing
"""

import httpx
import asyncio
import uuid
import time
from datetime import datetime, date

# Configuration - adjust for local vs GCP testing
BASE_URL = "http://127.0.0.1:8000/api/v1"  # Local
# BASE_URL = "https://dental-backend-xxx.run.app/api/v1"  # GCP

TEST_EMAIL = f"summary-test-{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "TestPassword123!"


async def main():
    print("=" * 60)
    print("QA TEST: Note Summary Pipeline")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}")
    print()
    
    state = {
        "access_token": None,
        "api_key": None,
        "patient_id": None,
        "visit_id": None,
        "note_id": None,
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # ============================================================
        # SETUP: Register and get auth
        # ============================================================
        print("🔧 SETUP: Creating test user and office...")
        
        # Register
        response = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "office": {"name": "Summary Test Office", "address": "123 Test St"},
                "user": {"email": TEST_EMAIL, "password": TEST_PASSWORD, "full_name": "Summary Tester"}
            }
        )
        if response.status_code != 200:
            print(f"❌ Registration failed: {response.text}")
            return
        
        data = response.json()
        state["access_token"] = data.get("access_token")
        print(f"   ✅ Registered user, got token")
        
        # Create API Key
        response = await client.post(
            f"{BASE_URL}/auth/keys",
            headers={"Authorization": f"Bearer {state['access_token']}"},
            json={"name": "Summary Test Key"}
        )
        if response.status_code == 200:
            state["api_key"] = response.json().get("key")
            print(f"   ✅ Created API key")
        
        headers = {"Authorization": f"Bearer {state['access_token']}"}
        
        # ============================================================
        # STEP 1: Create Patient
        # ============================================================
        print("\n📋 STEP 1: Creating patient...")
        
        response = await client.post(
            f"{BASE_URL}/patients",
            headers=headers,
            json={
                "first_name": "Summary",
                "last_name": "TestPatient",
                "dob": "1990-01-15",
                "contact_info": {"phone": "555-0000"}
            }
        )
        if response.status_code != 200:
            print(f"❌ Patient creation failed: {response.text}")
            return
        
        state["patient_id"] = response.json().get("id")
        print(f"   ✅ Created patient: {state['patient_id']}")
        
        # ============================================================
        # STEP 2: Create Visit
        # ============================================================
        print("\n📅 STEP 2: Creating visit...")
        
        response = await client.post(
            f"{BASE_URL}/visits",
            headers=headers,
            json={
                "patient_id": state["patient_id"],
                "visit_date": datetime.now().isoformat(),
                "reason": "Summary test visit",
                "status": "SCHEDULED"
            }
        )
        if response.status_code != 200:
            print(f"❌ Visit creation failed: {response.text}")
            return
        
        state["visit_id"] = response.json().get("id")
        print(f"   ✅ Created visit: {state['visit_id']}")
        
        # ============================================================
        # STEP 3: Check NO summary exists yet
        # ============================================================
        print("\n🔍 STEP 3: Verifying no summary exists yet...")
        
        response = await client.get(
            f"{BASE_URL}/patients/{state['patient_id']}/summary",
            headers=headers
        )
        if response.status_code == 404:
            print(f"   ✅ Confirmed: No summary yet (expected 404)")
        else:
            print(f"   ⚠️ Unexpected: summary already exists or error: {response.status_code}")
        
        # ============================================================
        # STEP 4: Create Note (triggers summary generation)
        # ============================================================
        print("\n📝 STEP 4: Creating note (should trigger summary generation)...")
        
        note_content = """
        Chief Complaint: Patient presents with sensitivity in upper right molar (#14).
        
        History: Sensitivity started 2 weeks ago, worse with cold drinks and sweets.
        No spontaneous pain. Previous filling on this tooth 3 years ago.
        
        Clinical Findings:
        - Tooth #14: Large distal carious lesion visible
        - Percussion: Mild sensitivity
        - Cold test: Lingering response ~5 seconds
        
        Assessment: Reversible pulpitis secondary to caries
        
        Plan:
        1. Excavate caries and restore with composite
        2. Review in 2 weeks for sensitivity check
        3. If symptoms persist, consider RCT
        """
        
        start_time = time.time()
        response = await client.post(
            f"{BASE_URL}/notes",
            headers=headers,
            json={
                "patient_id": state["patient_id"],
                "visit_id": state["visit_id"],
                "content": note_content,
                "note_type": "clinical",
                "area_of_oral_cavity": "Upper Right",
                "tooth_number": "14",
                "surface_ids": "O,D"
            }
        )
        elapsed = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ Note creation failed: {response.text}")
            return
        
        state["note_id"] = response.json().get("id")
        print(f"   ✅ Created note: {state['note_id']}")
        print(f"   ⏱️ Response time: {elapsed:.2f}s (includes sync summary if enabled)")
        
        # ============================================================
        # STEP 5: Verify summary was generated
        # ============================================================
        print("\n🎯 STEP 5: Checking for generated summary...")
        
        # For sync mode, summary should exist immediately
        # For async mode, we need to poll
        max_retries = 10
        retry_delay = 2  # seconds
        summary_found = False
        
        for attempt in range(max_retries):
            response = await client.get(
                f"{BASE_URL}/patients/{state['patient_id']}/summary",
                headers=headers
            )
            
            if response.status_code == 200:
                summary_found = True
                summary_data = response.json()
                break
            elif response.status_code == 404:
                if attempt < max_retries - 1:
                    print(f"   ⏳ Attempt {attempt + 1}/{max_retries}: Summary not ready, waiting {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
            else:
                print(f"   ❌ Unexpected error: {response.status_code} - {response.text}")
                break
        
        if summary_found:
            print(f"\n   ✅ SUMMARY GENERATED SUCCESSFULLY!")
            print(f"   ├── ID: {summary_data.get('id')}")
            print(f"   ├── Source: {summary_data.get('source')}")
            print(f"   ├── Model: {summary_data.get('model_name')}")
            print(f"   ├── Prompt Version: {summary_data.get('prompt_version')}")
            
            content = summary_data.get("content", {})
            summary_md = content.get("summary_markdown", "")
            if summary_md:
                preview = summary_md[:200].replace("\n", " ")
                print(f"   └── Content Preview: {preview}...")
            else:
                print(f"   └── Content: {content}")
        else:
            print(f"\n   ❌ SUMMARY NOT FOUND after {max_retries} attempts!")
            print(f"   └── This is the bug we're debugging. Check:")
            print(f"       1. Is SUMMARY_SYNC_MODE=true in .env?")
            print(f"       2. Is OPENAI_API_KEY set and valid?")
            print(f"       3. Check backend logs for errors")
        
        # ============================================================
        # STEP 6: Check summary history
        # ============================================================
        if summary_found:
            print("\n📚 STEP 6: Checking summary history...")
            
            response = await client.get(
                f"{BASE_URL}/patients/{state['patient_id']}/summary/history",
                headers=headers
            )
            
            if response.status_code == 200:
                history = response.json()
                print(f"   ✅ History endpoint working: {history.get('total', 0)} entries")
            else:
                print(f"   ⚠️ History endpoint issue: {response.status_code}")
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 60)
        if summary_found:
            print("✅ TEST PASSED: Summary pipeline working correctly!")
        else:
            print("❌ TEST FAILED: Summary not generated")
        print("=" * 60)
        print(f"""
Resources Created:
  Patient ID: {state['patient_id']}
  Visit ID:   {state['visit_id']}
  Note ID:    {state['note_id']}
""")


if __name__ == "__main__":
    asyncio.run(main())
