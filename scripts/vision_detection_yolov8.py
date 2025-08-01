from ultralytics import YOLO
import cv2
import requests
import time
import face_recognition
import os

# Load YOLOv8 model (nano for speed, or use yolov8s.pt for more accuracy)
model = YOLO('yolov8n.pt')

# Load known faces
known_face_encodings = []
known_face_names = []
for filename in os.listdir('known_faces'):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        image = face_recognition.load_image_file(f'known_faces/{filename}')
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_face_encodings.append(encoding[0])
            known_face_names.append(os.path.splitext(filename)[0])

# Camera setup (0 for default webcam, or use IP camera URL)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Flask backend URLs
BACKEND_URL = 'http://127.0.0.1:5050/api/vision-alert'
LATEST_FRAME_URL = 'http://127.0.0.1:5050/api/latest-frame'
DELETE_FRAMES_URL = 'http://127.0.0.1:5050/api/delete-alert-frames'

last_object_time = {}
object_timeout = 10  # seconds

# Helper to post a frame to the backend for streaming
def post_latest_frame(frame):
    _, img_encoded = cv2.imencode('.jpg', frame)
    files = {'frame': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
    try:
        requests.post(LATEST_FRAME_URL, files=files, timeout=0.5)
    except Exception:
        pass

# Helper to send 5 frames as alert
def send_suspicious_alert(frames, message):
    # Delete old frames first
    try:
        requests.post(DELETE_FRAMES_URL, timeout=1)
    except Exception:
        pass
    files = {}
    for i, frame in enumerate(frames):
        _, img_encoded = cv2.imencode('.jpg', frame)
        files[f'frame{i}'] = (f'frame{i}.jpg', img_encoded.tobytes(), 'image/jpeg')
    data = {'alert_type': 'suspicious', 'message': message}
    try:
        requests.post(BACKEND_URL, data=data, files=files, timeout=2)
    except Exception as e:
        print('Failed to send alert:', e)

suspicious_cooldown = 10  # seconds between suspicious alerts
last_suspicious_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Post frame for live streaming
    post_latest_frame(frame)

    # Run YOLOv8 inference
    results = model(frame)[0]
    detected_objects = set()
    person_detected = False

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        detected_objects.add(label)
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        color = (0,255,0) if label == 'person' else (255,0,0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        if label == 'person':
            person_detected = True

    # Alert if person detected when cabinet is open (simulate with a variable or input)
    cabinet_open = True  # TODO: Replace with real status from backend or GPIO
    if person_detected and cabinet_open:
        pass  # You can add a person alert here if needed

    # After detected_objects and person_detected are set
    if person_detected and 'cell phone' in detected_objects:
        # Send alert for phone held by a person
        data = {'alert_type': 'info', 'message': 'Phone held by a person'}
        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'frame0': ('frame0.jpg', img_encoded.tobytes(), 'image/jpeg')}
        try:
            requests.post(BACKEND_URL, data=data, files=files, timeout=1)
        except Exception as e:
            print('Failed to send phone-held alert:', e)

    # Track objects (e.g., 'cell phone', 'bottle', etc.)
    tracked_items = {'cell phone', 'bottle', 'laptop', 'book', 'cup', 'remote', 'scissors', 'mouse', 'keyboard'}
    now = time.time()
    for obj in tracked_items:
        if obj in detected_objects:
            last_object_time[obj] = now
        elif obj in last_object_time and now - last_object_time[obj] > object_timeout:
            # You can add an object missing alert here if needed
            del last_object_time[obj]

    # Suspicious movement (very basic: person + no object, or object on floor)
    if person_detected and not any(obj in detected_objects for obj in tracked_items):
        if now - last_suspicious_time > suspicious_cooldown:
            # Capture 5 frames over 2 seconds
            alert_frames = [frame]
            for _ in range(4):
                time.sleep(0.4)
                ret2, frame2 = cap.read()
                if ret2:
                    post_latest_frame(frame2)
                    alert_frames.append(frame2)
            send_suspicious_alert(alert_frames, 'Suspicious movement: person present, no tracked object visible')
            last_suspicious_time = now

    # Face recognition
    try:
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = []
        if face_locations:
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                # Optional: send an alert if your face is recognized
                # data = {'alert_type': 'info', 'message': f'{name} recognized'}
                # _, img_encoded = cv2.imencode('.jpg', frame)
                # files = {'frame0': ('frame0.jpg', img_encoded.tobytes(), 'image/jpeg')}
                # try:
                #     requests.post(BACKEND_URL, data=data, files=files, timeout=1)
                # except Exception as e:
                #     print('Failed to send face recognition alert:', e)
            # Draw a box and label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    except Exception as e:
        print('Face recognition error:', e)

    cv2.imshow('YOLOv8 Detection', frame)
    if cv2.waitKey(1) == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows() 