import requests
import json

def test_supervisor_login():
    """Test supervisor login"""
    url = "http://localhost:5000/api/employee-login"
    data = {"username": "supervisor", "password": "supervisor"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Supervisor login response: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_operator_login():
    """Test operator login"""
    url = "http://localhost:5000/api/employee-login"
    data = {"username": "Alaa Jouida", "password": "EMP001"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Operator login response: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invalid_login():
    """Test invalid login"""
    url = "http://localhost:5000/api/employee-login"
    data = {"username": "invalid", "password": "invalid"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Invalid login response: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 401
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Simple Login System ===")
    
    # Test 1: Supervisor login
    print("\n1. Testing supervisor login...")
    if test_supervisor_login():
        print("✅ Supervisor login successful")
    else:
        print("❌ Supervisor login failed")
    
    # Test 2: Operator login
    print("\n2. Testing operator login...")
    if test_operator_login():
        print("✅ Operator login successful")
    else:
        print("❌ Operator login failed")
    
    # Test 3: Invalid login
    print("\n3. Testing invalid login...")
    if test_invalid_login():
        print("✅ Invalid login correctly rejected")
    else:
        print("❌ Invalid login not properly handled")
    
    print("\n=== Test Complete ===")
    print("\n📋 Login Credentials:")
    print("Supervisor: username='supervisor', password='supervisor'")
    print("Operators: username='name', password='employee_ID'")
    print("Examples:")
    print("- Alaa Jouida / EMP001")
    print("- Taher Jouida / EMP002")
    print("- Ahmed Abdi / EMP003") 