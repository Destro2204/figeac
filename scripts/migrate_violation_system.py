#!/usr/bin/env python3
"""
Migration script to add violation prevention system
- Adds EmployeeInstrument table
- Adds action column to AccessLog table
"""

from app import app, db
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        # Create EmployeeInstrument table
        try:
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS employee_instrument (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fingerprint_ID INTEGER NOT NULL,
                        instrument_id INTEGER NOT NULL,
                        taken_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (fingerprint_ID) REFERENCES employee (fingerprint_ID),
                        FOREIGN KEY (instrument_id) REFERENCES instrument (id),
                        UNIQUE(fingerprint_ID, instrument_id)
                    )
                """))
                conn.commit()
            print("✅ EmployeeInstrument table created successfully")
        except Exception as e:
            print(f"⚠️ EmployeeInstrument table creation: {e}")
        
        # Add action column to AccessLog table
        try:
            with db.engine.connect() as conn:
                # Check if column exists
                result = conn.execute(text("PRAGMA table_info(access_log)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'action' not in columns:
                    conn.execute(text("ALTER TABLE access_log ADD COLUMN action VARCHAR(100)"))
                    conn.commit()
                    print("✅ Action column added to AccessLog table")
                else:
                    print("ℹ️ Action column already exists in AccessLog table")
        except Exception as e:
            print(f"⚠️ Action column addition: {e}")
        
        print("🎉 Migration completed!")

if __name__ == "__main__":
    migrate_database() 