import requests
import json

def test_employee_login_and_dashboard():
    """Test employee login and dashboard access"""
    session = requests.Session()
    
    # Test 1: Employee login
    print("1. Testing employee login...")
    login_data = {"username": "Alaa Jouida", "password": "EMP001"}
    
    try:
        response = session.post("http://localhost:5000/api/employee-login", json=login_data)
        print(f"Login status: {response.status_code}")
        print(f"Login response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Employee login successful")
            
            # Test 2: Access employee dashboard
            print("\n2. Testing employee dashboard access...")
            dashboard_response = session.get("http://localhost:5000/employee-dashboard")
            print(f"Dashboard status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✅ Employee dashboard accessible")
            else:
                print("❌ Employee dashboard not accessible")
                
        else:
            print("❌ Employee login failed")
            
    except Exception as e:
        print(f"Error: {e}")

def test_admin_dashboard_access():
    """Test that employees cannot access admin dashboard"""
    session = requests.Session()
    
    # First login as employee
    print("\n3. Testing employee access to admin dashboard...")
    login_data = {"username": "Alaa Jouida", "password": "EMP001"}
    
    try:
        response = session.post("http://localhost:5000/api/employee-login", json=login_data)
        
        if response.status_code == 200:
            # Try to access admin dashboard
            dashboard_response = session.get("http://localhost:5000/dashboard")
            print(f"Admin dashboard access status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 302:  # Redirect
                print("✅ Employee correctly redirected from admin dashboard")
            else:
                print("❌ Employee can access admin dashboard (should be blocked)")
        else:
            print("❌ Employee login failed for admin dashboard test")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("=== Testing Employee Dashboard System ===")
    test_employee_login_and_dashboard()
    test_admin_dashboard_access()
    print("\n=== Test Complete ===") 