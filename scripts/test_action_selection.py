#!/usr/bin/env python3
"""
Test the action selection feature
"""

import requests

def test_action_selection():
    print("🧪 Testing Action Selection Feature")
    print("=" * 40)
    
    # Test 1: Take instrument with explicit action
    print("\n1️⃣ Testing: Take instrument")
    response = requests.put("http://localhost:5050/api/instruments/1", json={
        "status": "taken",
        "fingerprint_ID": 1,
        "action": "take"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Return instrument with explicit action
    print("\n2️⃣ Testing: Return instrument")
    response = requests.put("http://localhost:5050/api/instruments/1", json={
        "status": "available",
        "fingerprint_ID": 1,
        "action": "return"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Check access logs for detailed actions
    print("\n3️⃣ Testing: Check access logs for detailed actions")
    logs = requests.get("http://localhost:5050/api/access-logs").json()
    print("Recent logs:")
    for log in logs[-3:]:
        print(f"  {log['name']} ({log['status']}): {log['action']}")
    
    print("\n✅ Action selection test completed!")

if __name__ == "__main__":
    test_action_selection() 