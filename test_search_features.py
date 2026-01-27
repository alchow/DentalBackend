import httpx
import asyncio
import uuid
from datetime import date, datetime
import time

BASE_URL = "http://localhost:8000/api/v1"

async def main():
    headers = {"x-api-key": "secret-key"}
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30.0) as client:
        print("--- Testing Dental Notes Backend: New Features & Search ---")

        # 1. Create Patient with Medical History
        print("\n1. Creating Patient with Medical History...")
        patient_data = {
            "first_name": "Test",
            "last_name": "Searcher",
            "dob": "1990-01-01",
            "medical_history": {
                "allergies": ["Penicillin", "Latex"],
                "conditions": ["Hypertension"]
            }
        }
        r = await client.post("/patients", json=patient_data)
        if r.status_code != 200:
            print(f"Error: {r.text}")
            return
        patient = r.json()
        patient_id = patient["id"]
        print(f"   Success! History: {patient['medical_history']}")

        # 2. Create Tasks
        print("\n2. Creating Tasks...")
        task_data = {
            "patient_id": patient_id,
            "description": "Follow up on root canal referral",
            "priority": "HIGH",
            "due_date": datetime.now().date().isoformat()
        }
        r = await client.post("/tasks", json=task_data)
        assert r.status_code == 200
        print(f"   Task Created: {r.json()['description']}")

        # 3. Create Note with Note Type & Search Terms
        print("\n3. Creating Note (Indexing)...")
        note_content = "Patient presenting with severe toothache in lower left quadrant. Suspect pulpitis on #19."
        note_data = {
            "patient_id": patient_id,
            "content": note_content,
            "note_type": "EMERGENCY",
            "tooth_number": "19",
            "author_id": "dr_test"
        }
        r = await client.post("/notes", json=note_data)
        assert r.status_code == 200
        note_id = r.json()["id"]
        print(f"   Note Created: {note_id}")

        # Wait a moment for indexing (though it is synchronous in MVP)
        # time.sleep(1) 

        # 4. Test Search (Keyword)
        print("\n4. Testing Keyword Search (Blind Index)...")
        # Search for "#19" or "toothache"
        search_query = {
            "query": "#19",
            "limit": 5
        }
        r = await client.post("/search", json=search_query)
        results = r.json()
        print(f"   Search '#19': Found {len(results)} results")
        if len(results) > 0:
            print(f"   Result Content: {results[0]['content']}")
            assert "#19" in results[0]['content']
        else:
            print("   ⚠️ No results found for exact keyword.")

        # 5. Test Search (Semantic)
        print("\n5. Testing Semantic Search (Vectors)...")
        # Search for "pain" - should find "toothache" even if "pain" is not in text
        search_query = {
            "query": "pain",
            "limit": 5
        }
        r = await client.post("/search", json=search_query)
        results = r.json()
        print(f"   Search 'pain': Found {len(results)} results")
        found_semantic = False
        for res in results:
            if res['id'] == note_id:
                print(f"   ✅ Found our note via semantic match!")
                found_semantic = True
                break
        
        if not found_semantic:
            print("   ⚠️ Semantic search did not find the note. Check OpenAI key/Embeddings.")

        # 6. Quick Phrases
        print("\n6. Testing Quick Phrases...")
        phrase_data = {"text": "Patient tolerated procedure well.", "category": "General"}
        r = await client.post("/quick_phrases", json=phrase_data)
        print(f"   Phrase Created: {r.json()['text']}")

        print("\n--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
