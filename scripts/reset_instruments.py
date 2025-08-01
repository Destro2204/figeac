#!/usr/bin/env python3
"""
Script to reset all instruments to available status
"""

from app import app, db
from app import Instrument, EmployeeInstrument

def reset_instruments():
    with app.app_context():
        # Reset all instruments to available
        instruments = Instrument.query.all()
        for instrument in instruments:
            instrument.status = "available"
        
        # Clear all employee-instrument assignments
        EmployeeInstrument.query.delete()
        
        db.session.commit()
        print("✅ All instruments reset to available status")
        print("✅ All employee-instrument assignments cleared")
        
        # Show current status
        instruments = Instrument.query.all()
        print(f"\n📊 Current instrument status:")
        for inst in instruments:
            print(f"  - {inst.name}: {inst.status}")

if __name__ == "__main__":
    reset_instruments() 