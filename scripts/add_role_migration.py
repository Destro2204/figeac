from app import db, app
from sqlalchemy import text

with app.app_context():
    # Add role column to employee table
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE employee ADD COLUMN role VARCHAR(20) DEFAULT 'operator'"))
            conn.commit()
        print("Successfully added role column to employee table")
    except Exception as e:
        print(f"Column might already exist or error: {e}")
    
    # Update existing employees to have operator role
    try:
        with db.engine.connect() as conn:
            conn.execute(text("UPDATE employee SET role = 'operator' WHERE role IS NULL"))
            conn.commit()
        print("Updated existing employees to operator role")
    except Exception as e:
        print(f"Error updating existing employees: {e}")
    
    print("Role migration completed!") 