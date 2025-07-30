from app import db, Instrument, app

with app.app_context():
    # Delete all existing instruments
    Instrument.query.delete()
    db.session.commit()

    # Add 5 new instruments
    for i in range(1, 6):
        inst = Instrument(name=f"Instrument {i}", status="available")
        db.session.add(inst)
    db.session.commit()

print("Instrument table reset to 5 instruments (all available). Only the first two will be used by ESP32.") 