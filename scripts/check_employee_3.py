from app import db, Employee, app

with app.app_context():
    emp = Employee.query.filter_by(fingerprint_ID=3).first()
    if emp:
        print(f"Employee 3 exists: {emp.name} - Role: {emp.role}")
    else:
        print("Employee 3 does not exist")
    
    # List all employees
    employees = Employee.query.all()
    print("\nAll employees:")
    for emp in employees:
        print(f"- ID: {emp.fingerprint_ID}, Name: {emp.name}, Role: {emp.role}") 