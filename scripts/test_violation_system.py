#!/usr/bin/env python3
"""
Test script for the violation prevention system
"""

import requests
import json
import time

BASE_URL = "http://localhost:5050"

def test_violation_system():
    print("🧪 Testing Violation Prevention System")
    print("=" * 50)
    
    # Test 1: Employee takes first instrument (should succeed)
    print("\n1️⃣ Testing: Employee takes first instrument")
    response = requests.put(f"{BASE_URL}/api/instruments/1", json={
        "status": "taken",
        "fingerprint_ID": 1  # Alaa Jouida
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Same employee tries to take second instrument (should be denied)
    print("\n2️⃣ Testing: Same employee tries to take second instrument")
    response = requests.put(f"{BASE_URL}/api/instruments/2", json={
        "status": "taken",
        "fingerprint_ID": 1  # Alaa Jouida
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Different employee takes second instrument (should succeed)
    print("\n3️⃣ Testing: Different employee takes second instrument")
    response = requests.put(f"{BASE_URL}/api/instruments/2", json={
        "status": "taken",
        "fingerprint_ID": 2  # Different employee
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 4: First employee returns their instrument (should succeed)
    print("\n4️⃣ Testing: First employee returns their instrument")
    response = requests.put(f"{BASE_URL}/api/instruments/1", json={
        "status": "available",
        "fingerprint_ID": 1  # Alaa Jouida
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 5: First employee can now take another instrument (should succeed)
    print("\n5️⃣ Testing: First employee can now take another instrument")
    response = requests.put(f"{BASE_URL}/api/instruments/3", json={
        "status": "taken",
        "fingerprint_ID": 1  # Alaa Jouida
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 6: Check access logs
    print("\n6️⃣ Testing: Check access logs for violations")
    response = requests.get(f"{BASE_URL}/api/access-logs")
    logs = response.json()
    print(f"Total logs: {len(logs)}")
    for log in logs[-5:]:  # Show last 5 logs
        print(f"  - {log['name']} ({log['status']}): {log['action']}")
    
    print("\n✅ Violation system test completed!")

if __name__ == "__main__":
    test_violation_system() 