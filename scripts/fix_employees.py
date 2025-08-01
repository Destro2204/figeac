from app import db, Employee, app

with app.app_context():
    # Clear existing employees
    Employee.query.delete()
    db.session.commit()
    
    # Add all employees with correct roles
    employees = [
        {'fingerprint_ID': 1, 'employee_ID': 'EMP001', 'name': 'Alaa Jouida', 'role': 'operator'},
        {'fingerprint_ID': 2, 'employee_ID': 'EMP002', 'name': 'Taher Jouida', 'role': 'operator'},
        {'fingerprint_ID': 3, 'employee_ID': 'EMP003', 'name': 'Ahmed Abdi', 'role': 'supervisor'},
        {'fingerprint_ID': 4, 'employee_ID': 'EMP004', 'name': 'Factory Supervisor', 'role': 'supervisor'},
    ]
    
    for emp_data in employees:
        emp = Employee(**emp_data)
        db.session.add(emp)
    
    db.session.commit()
    print("Employees updated with correct roles:")
    for emp in employees:
        print(f"- {emp['name']} (ID: {emp['fingerprint_ID']}) - Role: {emp['role']}") 