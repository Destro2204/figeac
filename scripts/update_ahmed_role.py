from app import db, Employee, app

with app.app_context():
    # Find Ahmed Abdi and update his role to operator
    ahmed = Employee.query.filter_by(fingerprint_ID=3).first()
    if ahmed:
        ahmed.role = 'operator'
        db.session.commit()
        print(f"Updated {ahmed.name} role to: {ahmed.role}")
    else:
        print("Ahmed Abdi not found")
    
    # Verify all employees
    employees = Employee.query.order_by(Employee.fingerprint_ID).all()
    print("\nAll employees with updated roles:")
    for emp in employees:
        print(f"- {emp.name} (ID: {emp.fingerprint_ID}) - Role: {emp.role}") 