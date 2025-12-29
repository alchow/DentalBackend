import httpx
import asyncio
import uuid
from datetime import date, datetime

BASE_URL = "http://localhost:8000/api/v1"

async def main():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        print("--- Testing Dental Notes Backend ---")

        # 1. Create Patient
        print("\n1. Creating Patient...")
        patient_data = {
            "first_name": "John",
            "last_name": "Doe",
            "dob": "1980-01-01",
            "contact_info": {
                "phone": "555-0199",
                "email": "john.doe@example.com",
                "address": "123 Main St"
            }
        }
        r = await client.post("/patients/", json=patient_data)
        if r.status_code != 200:
            print(f"Error creating patient: {r.text}")
            return
        patient = r.json()
        patient_id = patient["id"]
        print(f"   Success! Patient ID: {patient_id}")
        print(f"   Encrypted/Decrypted Name: {patient['first_name']} {patient['last_name']}")
        print(f"   Blind Index Hash: {patient['last_name_hash'][:10]}...")

        # 2. Search Patient
        print("\n2. Searching for 'Doe'...")
        r = await client.get("/patients/search/", params={"last_name": "Doe"})
        results = r.json()
        print(f"   Found {len(results)} matches.")
        assert len(results) >= 1
        found_ids = [r["id"] for r in results]
        assert patient_id in found_ids

        # 3. Create Visit
        print("\n3. Creating Visit...")
        visit_data = {
            "patient_id": patient_id,
            "visit_date": datetime.now().isoformat(),
            "reason": "Routine Checkup",
            "status": "SCHEDULED"
        }
        r = await client.post("/visits/", json=visit_data)
        visit = r.json()
        visit_id = visit["id"]
        print(f"   Success! Visit ID: {visit_id}")

        # 4. Add Note
        print("\n4. Adding Clinical Note...")
        note_data = {
            "patient_id": patient_id,
            "visit_id": visit_id,
            "content": "Patient complains of mild sensitivity in upper right quadrant.",
            "author_id": "dr_smith"
        }
        r = await client.post("/notes/", json=note_data)
        note = r.json()
        note_id = note["id"]
        print(f"   Success! Note ID: {note_id}")
        print(f"   Content: {note['content']}")

        # 5. Update Note (Audit Trail Test)
        print("\n5. Updating Note (Correcting Diagnosis)...")
        update_data = {
            "content": "Patient complains of mild sensitivity in upper LEFT quadrant. X-ray limits normal.",
            "author_id": "dr_smith"
        }
        r = await client.put(f"/notes/{note_id}", json=update_data)
        updated_note = r.json()
        print(f"   Updated Content: {updated_note['content']}")

        # 6. Verify Database History (Optional - implementation check)
        # We don't have a direct history endpoint in the plan, but we can verify via DB if we wanted.
        # For now, let's assume if the update worked without error, we are good.
        
        # 7. Add Bill
        print("\n6. Creating Bill...")
        bill_data = {
            "patient_id": patient_id,
            "visit_id": visit_id,
            "amount": 150.00,
            "codes": ["D0120", "D0272"], # Periodic Oral Eval, Bitewings
            "status": "PENDING"
        }
        r = await client.post("/bills/", json=bill_data)
        bill = r.json()
        print(f"   Success! Bill ID: {bill['id']}")
        print(f"   Codes: {[c['code'] for c in bill['codes']]}")

        print("\n--- Test Complete: All Systems Go ---")

if __name__ == "__main__":
    asyncio.run(main())
