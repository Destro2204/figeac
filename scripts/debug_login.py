import requests
import json

def test_login_with_exact_data():
    """Test login with the exact data format"""
    url = "http://localhost:5000/api/employee-login"
    
    # Test 1: Correct format
    data1 = {"username": "Alaa Jouida", "password": "EMP001"}
    print("Testing with correct format:")
    print(f"Data: {data1}")
    
    try:
        response = requests.post(url, json=data1)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("---")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Old fingerprint format (to see the error)
    data2 = {"fingerprint_ID": 1}
    print("Testing with old fingerprint format:")
    print(f"Data: {data2}")
    
    try:
        response = requests.post(url, json=data2)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login_with_exact_data() 