import requests
import sys

# Since we are running outside docker, we need to know where the server is running.
# Assuming running locally for test on 8080 or port forwarded from Cloud Run.
# Ideally we test unit test, but integration test with requests is faster here.

BASE_URL = "http://localhost:8000" # Local Uvicorn default

def test_auth():
    print(f"Testing Auth against {BASE_URL}...")
    
    # 1. Test Public Endpoint (Health) - Should Fail? actually Health is outside router
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"Health Check (Public): {r.status_code}") 
    except Exception as e:
        print(f"Server might not be running at {BASE_URL}: {e}")
        return

    # 2. Test Secured Endpoint WITHOUT Key
    r = requests.get(f"{BASE_URL}/api/v1/patients/search/?last_name=test")
    print(f"Secured Endpoint (No Key): {r.status_code}")
    if r.status_code == 403:
        print("✅ PASS: Access Denied as expected.")
    else:
        print(f"❌ FAIL: Expected 403, got {r.status_code}")

    # 3. Test Secured Endpoint WITH Key
    headers = {"X-API-Key": "secret-key"} # Default dev key
    r = requests.get(f"{BASE_URL}/api/v1/patients/search/?last_name=test", headers=headers)
    print(f"Secured Endpoint (With Key): {r.status_code}")
    if r.status_code == 200:
        print("✅ PASS: Access Granted.")
    elif r.status_code == 403:
        print("❌ FAIL: Key rejected.")
    else:
        print(f"⚠️ NOTE: Got {r.status_code} (might be other error like DB connection, but Auth passed if not 403)")

if __name__ == "__main__":
    test_auth()
