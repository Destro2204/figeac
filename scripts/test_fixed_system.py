#!/usr/bin/env python3
"""
Test the fixed violation prevention system
"""

import requests
import time

def test_fixed_system():
    print("🧪 Testing Fixed Violation Prevention System")
    print("=" * 50)
    
    # Test 1: Take first instrument
    print("\n1️⃣ Testing: Take first instrument")
    response = requests.put("http://localhost:5050/api/instruments/1", json={
        "status": "taken",
        "fingerprint_ID": 1
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Try to take second instrument (should be denied)
    print("\n2️⃣ Testing: Try to take second instrument (should be denied)")
    response = requests.put("http://localhost:5050/api/instruments/2", json={
        "status": "taken",
        "fingerprint_ID": 1
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Return first instrument
    print("\n3️⃣ Testing: Return first instrument")
    response = requests.put("http://localhost:5050/api/instruments/1", json={
        "status": "available",
        "fingerprint_ID": 1
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 4: Now can take second instrument
    print("\n4️⃣ Testing: Now can take second instrument")
    response = requests.put("http://localhost:5050/api/instruments/2", json={
        "status": "taken",
        "fingerprint_ID": 1
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("\n✅ Fixed system test completed!")

if __name__ == "__main__":
    test_fixed_system() 