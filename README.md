# Smart Cabinet System

A comprehensive industrial instrument management system with fingerprint authentication, real-time monitoring, and multi-instrument prevention.

## 🚀 Features

- **🔐 Fingerprint Authentication** - Secure employee identification
- **🛡️ Multi-Instrument Prevention** - One instrument per employee rule
- **📊 Real-time Dashboard** - Admin monitoring with live alerts
- **👥 Role-based Access** - Admin, supervisor, and operator roles
- **🔧 ESP32 Integration** - Hardware control and feedback
- **📱 Responsive UI** - Factory-friendly dark theme

## 📁 Project Structure

```
figeac/
├── app.py                 # Main Flask application
├── templates/            # HTML templates (dashboard, login)
├── static/              # CSS, JS, images, alerts
├── esp32/               # ESP32 firmware and configuration
├── scripts/             # Utility and test scripts
├── docs/                # Documentation
├── tests/               # Unit tests
├── models/              # ML models (YOLOv8)
├── known_faces/         # Face recognition database
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python scripts/migrate_violation_system.py
python scripts/reset_instruments.py
```

### 3. Start Server
```bash
python app.py
```

### 4. Upload ESP32 Firmware
- Open `esp32/` in PlatformIO
- Configure WiFi settings in `esp32/src/main.cpp`
- Upload to ESP32 device

### 5. Access Dashboard
- **Admin Dashboard**: `http://localhost:5050/dashboard`
- **Employee Dashboard**: `http://localhost:5050/employee-dashboard`

## 🔧 Configuration

### ESP32 Settings
Edit `esp32/src/main.cpp`:
```cpp
const char *ssid = "YOUR_WIFI_SSID";
const char *password = "YOUR_WIFI_PASSWORD";
const char *server = "http://YOUR_SERVER_IP:5050";
```

### Database
- SQLite database: `instance/employees.db`
- Auto-created on first run
- Migration scripts in `scripts/`

## 📊 System Components

### Backend (Flask)
- **Authentication**: Fingerprint and username/password
- **API Endpoints**: RESTful instrument management
- **Real-time Updates**: Server-Sent Events (SSE)
- **Violation Prevention**: Multi-instrument tracking

### Frontend (Bootstrap)
- **Admin Dashboard**: Multi-cabinet monitoring
- **Employee Dashboard**: Simplified interface
- **Real-time Alerts**: Violation notifications
- **Responsive Design**: Mobile-friendly

### Hardware (ESP32)
- **Fingerprint Sensor**: Employee identification
- **Relay Control**: Door/lock management
- **Button Interface**: Instrument selection
- **WiFi Communication**: HTTP API calls

## 🧪 Testing

### Run System Tests
```bash
python scripts/test_violation_system.py
python scripts/test_fixed_system.py
python scripts/test_action_selection.py
```

### Check System Status
```bash
python scripts/check_logs.py
python scripts/check_employees.py
```

## 📝 API Documentation

### Authentication
- `POST /api/employee-login` - Employee login
- `POST /api/admin-login` - Admin login

### Instruments
- `GET /api/instruments` - List all instruments
- `PUT /api/instruments/<id>` - Update instrument status

### Access Logs
- `GET /api/access-logs` - View access history
- `POST /api/access-log` - Log access attempt

### Real-time Events
- `GET /events/violation-alert` - Violation notifications
- `GET /events/access-log` - Live access updates

## 🔒 Security Features

- **Fingerprint Authentication**: Biometric security
- **Role-based Access**: Different permission levels
- **Multi-instrument Prevention**: Resource management
- **Real-time Monitoring**: Live violation detection
- **Audit Logging**: Complete access history

## 🏭 Factory Integration

- **High-contrast UI**: Optimized for factory lighting
- **Touch-friendly Interface**: Large buttons and text
- **Offline Capability**: ESP32 local operation
- **Scalable Architecture**: Multi-cabinet support

## 📞 Support

For issues and questions:
1. Check the `docs/` directory for detailed documentation
2. Review `scripts/` for utility functions
3. Test with provided scripts in `scripts/`

## 📄 License

This project is designed for industrial use with proper security measures and audit trails.
