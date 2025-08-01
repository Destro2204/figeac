from app import db, Employee, app

with app.app_context():
    # Add Ahmed Abdi
    ahmed = Employee(
        fingerprint_ID=3,
        employee_ID='EMP003',
        name='Ahmed Abdi',
        role='operator'
    )
    db.session.add(ahmed)
    db.session.commit()
    print("Added Ahmed Abdi as supervisor")
    
    # Verify all employees
    employees = Employee.query.all()
    print("\nAll employees in database:")
    for emp in employees:
        print(f"- {emp.name} (ID: {emp.fingerprint_ID}) - Role: {emp.role}") 