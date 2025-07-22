from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, Response, stream_with_context, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import time
import queue
import json
import os
from threading import Lock

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Needed for session management
db = SQLAlchemy(app)

# Global variable to store door status
door_status = "closed"
# Global list of queues for access log SSE clients
access_log_clients = []
# Global list of queues for vision alert SSE clients
vision_alert_clients = []
# Global variable to store the latest frame for MJPEG streaming
latest_frame = None
latest_frame_lock = Lock()

class Employee(db.Model):
    fingerprint_ID = db.Column(db.Integer, primary_key=True)
    employee_ID = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    access_logs = db.relationship('AccessLog', backref='employee', lazy=True)

class Instrument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # "available" or "taken"
    access_logs = db.relationship('AccessLog', backref='instrument', lazy=True)

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fingerprint_ID = db.Column(db.Integer, db.ForeignKey('employee.fingerprint_ID'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'))  # NEW COLUMN

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


@app.route("/", methods=["GET", "POST"])
def home():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return render_template("home.html")
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

@app.route("/about")
def about():
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('home'))
    return render_template("about.html")

@app.route('/dashboard')
def dashboard():
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('home'))
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).all()
    log_data = []
    for log in logs:
        employee = Employee.query.filter_by(fingerprint_ID=log.fingerprint_ID).first()
        instrument = Instrument.query.filter_by(id=log.instrument_id).first() if log.instrument_id else None
        log_data.append({
            'id': log.id,
            'employee_ID': employee.employee_ID if employee else None,
            'name': employee.name if employee else None,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status': log.status,
            'instrument_id': instrument.id if instrument else None,
            'instrument_name': instrument.name if instrument else None
        })
    return render_template('dashboard.html', logs=log_data)
 

@app.route('/api/verify', methods=['POST'])
def verify_fingerprint():
    data = request.get_json()
    fingerprint_ID = data.get('fingerprint_ID')
    if fingerprint_ID is None:
        return jsonify({'status': 'failure', 'message': 'fingerprint_ID is required', 'access': 'denied'}), 400
    employee = Employee.query.filter_by(fingerprint_ID=fingerprint_ID).first()
    if employee:
        return jsonify({
            'status': 'success',
            'employee': {
                'fingerprint_ID': employee.fingerprint_ID,
                'employee_ID': employee.employee_ID,
                'name': employee.name
            },
            'access': 'allowed'
        })
    else:
        return jsonify({'status': 'failure', 'access': 'denied'}), 404


@app.route('/api/access-log', methods=['POST'])
def log_access():
    data = request.get_json()
    fingerprint_ID = data.get('fingerprint_ID')
    status = data.get('status')
    instrument_id = data.get('instrument_id')  # NEW

    if fingerprint_ID is None or status is None or instrument_id is None:
        return jsonify({'status': 'failure', 'message': 'fingerprint_ID, status, and instrument_id are required'}), 400

    employee = Employee.query.filter_by(fingerprint_ID=fingerprint_ID).first()
    instrument = Instrument.query.filter_by(id=instrument_id).first()
    if not employee:
        return jsonify({'status': 'failure', 'message': 'Employee not found'}), 404
    if not instrument:
        return jsonify({'status': 'failure', 'message': 'Instrument not found'}), 404

    access_log = AccessLog(fingerprint_ID=fingerprint_ID, status=status, instrument_id=instrument_id)
    db.session.add(access_log)
    db.session.commit()
    # Real-time SSE push
    log_data = {
        'id': access_log.id,
        'fingerprint_ID': access_log.fingerprint_ID,
        'employee_ID': employee.employee_ID if employee else None,
        'name': employee.name if employee else None,
        'status': access_log.status,
        'timestamp': access_log.timestamp.isoformat(),
        'instrument_id': instrument.id,
        'instrument_name': instrument.name
    }
    for client in access_log_clients:
        client.put(json.dumps(log_data))
    return jsonify({'status': 'success', 'message': 'Access log added'})


@app.route('/api/access-logs', methods=['GET'])
def get_access_logs():
    fingerprint_ID = request.args.get('fingerprint_ID', type=int)
    employee_ID = request.args.get('employee_ID', type=str)
    status = request.args.get('status', type=str)
    query = AccessLog.query
    if fingerprint_ID is not None and fingerprint_ID != '':
        query = query.filter_by(fingerprint_ID=fingerprint_ID)
    if status:
        query = query.filter_by(status=status)
    logs = query.order_by(AccessLog.timestamp.desc()).all()
    result = []
    for log in logs:
        employee = Employee.query.filter_by(fingerprint_ID=log.fingerprint_ID).first()
        instrument = Instrument.query.filter_by(id=log.instrument_id).first() if log.instrument_id else None
        if employee_ID and (not employee or employee.employee_ID != employee_ID):
            continue
        result.append({
            'id': log.id,
            'fingerprint_ID': log.fingerprint_ID,
            'employee_ID': employee.employee_ID if employee else None,
            'name': employee.name if employee else None,
            'timestamp': log.timestamp.isoformat(),
            'status': log.status,
            'instrument_id': instrument.id if instrument else None,
            'instrument_name': instrument.name if instrument else None
        })
    return jsonify(result)


@app.route('/api/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    result = []
    for emp in employees:
        result.append({
            'fingerprint_ID': emp.fingerprint_ID,
            'employee_ID': emp.employee_ID,
            'name': emp.name
        })
    return jsonify(result)


@app.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.get_json()
    fingerprint_ID = data.get('fingerprint_ID')
    employee_ID = data.get('employee_ID')
    name = data.get('name')
    if not all([fingerprint_ID, employee_ID, name]):
        return jsonify({'status': 'failure', 'message': 'fingerprint_ID, employee_ID, and name are required'}), 400
    # Check for duplicate fingerprint_ID or employee_ID
    if Employee.query.filter_by(fingerprint_ID=fingerprint_ID).first() or Employee.query.filter_by(employee_ID=employee_ID).first():
        return jsonify({'status': 'failure', 'message': 'Employee with this fingerprint_ID or employee_ID already exists'}), 409
    new_employee = Employee(fingerprint_ID=fingerprint_ID, employee_ID=employee_ID, name=name)
    db.session.add(new_employee)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Employee added'})


@app.route('/api/employees/<int:fingerprint_ID>', methods=['DELETE'])
def delete_employee(fingerprint_ID):
    employee = Employee.query.filter_by(fingerprint_ID=fingerprint_ID).first()
    if not employee:
        return jsonify({'status': 'failure', 'message': 'Employee not found'}), 404
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Employee deleted'})


@app.route('/api/employees/<int:fingerprint_ID>', methods=['PUT'])
def update_employee(fingerprint_ID):
    data = request.get_json()
    employee = Employee.query.filter_by(fingerprint_ID=fingerprint_ID).first()
    if not employee:
        return jsonify({'status': 'failure', 'message': 'Employee not found'}), 404
    new_employee_ID = data.get('employee_ID')
    new_name = data.get('name')
    if not new_employee_ID or not new_name:
        return jsonify({'status': 'failure', 'message': 'employee_ID and name are required'}), 400
    # Check for duplicate employee_ID (but allow if it's the same as current)
    if new_employee_ID != employee.employee_ID and Employee.query.filter_by(employee_ID=new_employee_ID).first():
        return jsonify({'status': 'failure', 'message': 'Another employee with this employee_ID already exists'}), 409
    employee.employee_ID = new_employee_ID
    employee.name = new_name
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Employee updated'})


@app.route('/api/door-status', methods=['GET'])
def get_door_status():
    return jsonify({
        'status': 'closed',
        'message': 'This is a placeholder. Integrate with hardware for real status.'
    })

# POST endpoint to update door status
@app.route('/api/door-status', methods=['POST'])
def door_status_post():
    global door_status
    data = request.get_json()
    status = data.get('status')
    if status not in ['opened', 'closed']:
        return jsonify({'status': 'failure', 'message': 'Invalid status'}), 400
    door_status = status
    return jsonify({'status': 'success', 'message': f'Door status {status} set'})

# SSE endpoint for real-time door status
@app.route('/events')
def sse_events():
    def event_stream():
        last_status = None
        while True:
            if door_status != last_status:
                yield f"data: {door_status}\n\n"
                last_status = door_status
            time.sleep(1)
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/events/access-log')
def sse_access_log():
    def event_stream(q):
        while True:
            log = q.get()
            yield f"data: {log}\n\n"
    q = queue.Queue()
    access_log_clients.append(q)
    return Response(stream_with_context(event_stream(q)), mimetype="text/event-stream")

@app.route('/cabinet_stream')
def cabinet_stream():
    return render_template('cabinet_stream.html')

@app.route('/api/latest-frame', methods=['POST'])
def latest_frame_upload():
    global latest_frame
    if 'frame' not in request.files:
        return jsonify({'status': 'failure', 'message': 'No frame uploaded'}), 400
    frame = request.files['frame']
    with latest_frame_lock:
        latest_frame = frame.read()
    return jsonify({'status': 'success'})

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            with latest_frame_lock:
                frame = latest_frame
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                import time; time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/delete-alert-frames', methods=['POST'])
def delete_alert_frames():
    alert_dir = 'static/alerts/'
    if os.path.exists(alert_dir):
        for fname in os.listdir(alert_dir):
            fpath = os.path.join(alert_dir, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)
    return jsonify({'status': 'success', 'message': 'All alert frames deleted'})

@app.route('/api/vision-alert', methods=['POST'])
def vision_alert():
    # Delete old frames first
    alert_dir = 'static/alerts/'
    os.makedirs(alert_dir, exist_ok=True)
    for fname in os.listdir(alert_dir):
        fpath = os.path.join(alert_dir, fname)
        if os.path.isfile(fpath):
            os.remove(fpath)
    alert_type = request.form.get('alert_type')
    message = request.form.get('message')
    frame_urls = []
    # Accept up to 5 frames: frame0, frame1, ...
    for i in range(5):
        frame = request.files.get(f'frame{i}')
        if frame:
            frame_path = f'{alert_dir}{int(time.time())}_{i}.jpg'
            frame.save(frame_path)
            frame_urls.append('/' + frame_path.replace('\\', '/'))
    alert_data = {
        'alert_type': alert_type,
        'message': message,
        'frame_urls': frame_urls
    }
    for client in vision_alert_clients:
        client.put(json.dumps(alert_data))
    return jsonify({'status': 'success'})

@app.route('/events/vision-alert')
def sse_vision_alert():
    def event_stream(q):
        while True:
            alert = q.get()
            yield f"data: {alert}\n\n"
    q = queue.Queue()
    vision_alert_clients.append(q)
    return Response(stream_with_context(event_stream(q)), mimetype="text/event-stream")

@app.route('/api/instruments', methods=['GET'])
def get_instruments():
    instruments = Instrument.query.all()
    result = []
    for inst in instruments:
        result.append({
            'id': inst.id,
            'name': inst.name,
            'status': inst.status
        })
    return jsonify(result)

@app.route('/api/instruments', methods=['POST'])
def add_instrument():
    data = request.get_json()
    name = data.get('name')
    status = data.get('status', 'available')
    if not name:
        return jsonify({'status': 'failure', 'message': 'Instrument name is required'}), 400
    new_instrument = Instrument(name=name, status=status)
    db.session.add(new_instrument)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Instrument added'})

@app.route('/api/instruments/<int:instrument_id>', methods=['PUT'])
def update_instrument(instrument_id):
    data = request.get_json()
    instrument = Instrument.query.filter_by(id=instrument_id).first()
    if not instrument:
        return jsonify({'status': 'failure', 'message': 'Instrument not found'}), 404
    name = data.get('name')
    status = data.get('status')
    if name:
        instrument.name = name
    if status:
        instrument.status = status
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Instrument updated'})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin', password_hash=generate_password_hash('admin'))
            db.session.add(admin)
            db.session.commit()
    print("Database and tables created.")
    app.run(host="0.0.0.0", port=5050)
