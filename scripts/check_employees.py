from app import db, Employee, app

with app.app_context():
    employees = Employee.query.all()
    print("=== Current Employees in Database ===")
    print("Format: Name / Employee_ID (Fingerprint_ID)")
    print("-" * 50)
    
    for emp in employees:
        print(f"- {emp.name} / {emp.employee_ID} (ID: {emp.fingerprint_ID})")
    
    print("\n=== Login Credentials ===")
    print("For Employee Login:")
    print("Username: name")
    print("Password: employee_ID")
    print("\nExamples:")
    for emp in employees:
        print(f"- Username: '{emp.name}'")
        print(f"  Password: '{emp.employee_ID}'")
        print() 