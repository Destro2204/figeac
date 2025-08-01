import requests
import time

print("🧪 Testing Violation and New Logs")
print("=" * 40)

# First, take an instrument
print("1. Taking instrument 1...")
response = requests.put("http://localhost:5050/api/instruments/1", json={
    "status": "taken",
    "fingerprint_ID": 1
})
print(f"Status: {response.status_code}")

# Try to take another instrument (should be denied)
print("\n2. Trying to take instrument 2 (should be denied)...")
response = requests.put("http://localhost:5050/api/instruments/2", json={
    "status": "taken",
    "fingerprint_ID": 1
})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Check the latest logs
print("\n3. Checking latest logs...")
logs = requests.get("http://localhost:5050/api/access-logs").json()
for log in logs[-5:]:
    print(f"  {log['name']} ({log['status']}): {log['action']}") 