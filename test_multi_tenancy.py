import asyncio
import httpx
import uuid

BASE_URL = "http://localhost:8000/api/v1"

async def register_office(client: httpx.AsyncClient, name_suffix: str):
    email = f"dentist_{name_suffix}_{uuid.uuid4().hex[:6]}@example.com"
    password = "securepassword123"
    office_name = f"Office {name_suffix}"
    
    payload = {
        "office": {"name": office_name, "address": "123 Test St"},
        "user": {"email": email, "password": password, "full_name": f"Dr. {name_suffix}"}
    }
    r = await client.post("/auth/register", json=payload)
    if r.status_code != 200:
        print(f"❌ Register {name_suffix} Failed: {r.text}")
        return None, None
    print(f"✅ Registered {office_name} ({email})")
    return r.json()["access_token"], email

async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        print("--- 1. Registering Office A & B ---")
        token_a, email_a = await register_office(client, "A")
        token_b, email_b = await register_office(client, "B")
        
        if not token_a or not token_b:
            print("Registration failed. Aborting.")
            return

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 2. User A creates Patient A
        print("\n--- 2. User A creates Patient A ---")
        patient_a_payload = {
            "first_name": "Alice",
            "last_name": "Apple", # Something unique to test search? "Apple"
            "dob": "1990-01-01",
            "contact_info": {"phone": "555-0101"}
        }
        r = await client.post("/patients", json=patient_a_payload, headers=headers_a)
        if r.status_code != 200:
            print(f"❌ User A Create Patient Failed: {r.text}")
            return
        patient_a_id = r.json()["id"]
        print(f"✅ Patient A created: {patient_a_id}")

        # 3. User B tries to read Patient A
        print("\n--- 3. User B tries to read Patient A (Should Fail) ---")
        r = await client.get(f"/patients/{patient_a_id}", headers=headers_b)
        if r.status_code == 404:
            print("✅ User B could NOT read Patient A (404 as expected).")
        else:
            print(f"❌ User B COULD read Patient A! Status: {r.status_code}")

        # 4. User A searches "Apple" -> Should find
        print("\n--- 4. User A searches 'Apple' ---")
        r = await client.get("/patients/search/query?last_name=Apple", headers=headers_a)
        results = r.json()
        if len(results) > 0 and results[0]["id"] == patient_a_id:
             print(f"✅ User A found Patient A via search.")
        else:
             print(f"❌ User A could NOT find Patient A. Results: {results}")

        # 5. User B searches "Apple" -> Should NOT find
        print("\n--- 5. User B searches 'Apple' (Should Fail) ---")
        r = await client.get("/patients/search/query?last_name=Apple", headers=headers_b)
        results = r.json()
        if len(results) == 0:
             print(f"✅ User B found 0 results for 'Apple' (Correct).")
        else:
             print(f"❌ User B found Patient A! Results: {results}")

        # 6. Soft Delete Test
        print("\n--- 6. User A Soft Deletes Patient A ---")
        r = await client.delete(f"/patients/{patient_a_id}", headers=headers_a)
        if r.status_code == 204:
            print("✅ Patient A soft deleted.")
        else:
            print(f"❌ Soft Delete Failed: {r.status_code}")

        # 7. User A searches "Apple" again -> Should NOT find (Filtered out)
        print("\n--- 7. User A searches 'Apple' again (Should be empty) ---")
        r = await client.get("/patients/search/query?last_name=Apple", headers=headers_a)
        results = r.json()
        if len(results) == 0:
             print(f"✅ User A found 0 results after soft delete (Correct).")
        else:
             print(f"❌ User A found Patient A after soft delete! Results: {results}")

        print("\n--- Multi-Tenancy Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
