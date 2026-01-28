import asyncio
import httpx
import uuid

BASE_URL = "http://localhost:8000/api/v1"

async def main():
    email = f"dentist_{uuid.uuid4().hex[:8]}@example.com"
    password = "securepassword123"
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Register
        print(f"--- Registering {email} ---")
        register_payload = {
            "office": {"name": "Test Office", "address": "123 Test St"},
            "user": {"email": email, "password": password, "full_name": "Dr. Test"}
        }
        r = await client.post("/auth/register", json=register_payload)
        if r.status_code != 200:
            print(f"Register Failed: {r.text}")
            return
        token = r.json()["access_token"]
        print("✅ Registered. Token received.")
        
        # 2. Login (sanity check)
        print("\n--- Logging in ---")
        login_payload = {"email": email, "password": password}
        r = await client.post("/auth/login", json=login_payload)
        if r.status_code != 200:
             print(f"Login Failed: {r.text}")
             return
        print("✅ Login Successful.")
        
        # 3. Create API Key
        print("\n--- Creating API Key ---")
        headers = {"Authorization": f"Bearer {token}"}
        key_payload = {"name": "Zapier Integration"}
        r = await client.post("/auth/keys", json=key_payload, headers=headers)
        if r.status_code != 200:
            print(f"Create Key Failed: {r.text}")
            return
        key_data = r.json()
        print(f"✅ Key Created: {key_data['key']} (Prefix: {key_data['prefix']})")
        
        # 4. List Keys
        print("\n--- Listing Keys ---")
        r = await client.get("/auth/keys", headers=headers)
        if r.status_code != 200:
            print(f"List Keys Failed: {r.text}")
            return
        keys = r.json()
        print(f"✅ Found {len(keys)} keys.")
        print("--- Auth Flow Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
