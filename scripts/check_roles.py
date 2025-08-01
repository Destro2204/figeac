from app import db, Employee, app

with app.app_context():
    employees = Employee.query.order_by(Employee.fingerprint_ID).all()
    print("Current Employee Roles in Database:")
    for emp in employees:
        print(f"- Fingerprint ID: {emp.fingerprint_ID}, Employee ID: {emp.employee_ID}, Name: {emp.name}, Role: {emp.role}") 