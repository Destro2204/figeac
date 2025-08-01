# Smart Cabinet System Documentation

## System Overview
The Smart Cabinet System is a comprehensive solution for managing instrument access in industrial environments with fingerprint authentication and real-time monitoring.

## Key Features
- **Fingerprint Authentication** - Secure employee identification
- **Multi-Instrument Prevention** - One instrument per employee rule
- **Real-time Alerts** - Admin dashboard notifications
- **Role-based Access** - Admin, supervisor, and operator roles
- **ESP32 Integration** - Hardware control and feedback

## Architecture
- **Backend**: Flask web server with SQLite database
- **Frontend**: Bootstrap-based responsive dashboard
- **Hardware**: ESP32 with fingerprint sensor and relays
- **Communication**: HTTP REST API and Server-Sent Events

## Directory Structure
```
figeac/
├── app.py                 # Main Flask application
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── esp32/               # ESP32 firmware
├── scripts/             # Utility and test scripts
├── docs/                # Documentation
├── tests/               # Unit tests
└── requirements.txt     # Python dependencies
```

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run database migration: `python scripts/migrate_violation_system.py`
3. Start server: `python app.py`
4. Upload ESP32 firmware to device
5. Access dashboard at `http://localhost:5050` 