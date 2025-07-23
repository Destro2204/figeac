import face_recognition
import cv2
import os

# Load known faces
known_face_encodings = []
known_face_names = []

for filename in os.listdir('known_faces'):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        image = face_recognition.load_image_file(f'known_faces/{filename}')
        encoding = face_recognition.face_encodings(image)
        print(f"{filename}: {len(encoding)} encodings found")
        if encoding:
            known_face_encodings.append(encoding[0])
            known_face_names.append(os.path.splitext(filename)[0])
        else:
            print(f"Warning: No face found in {filename}")

print("Loaded known faces:", known_face_names)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame)
    print(f"Detected {len(face_locations)} face locations in frame")
    face_locations = [tuple(map(int, loc)) for loc in face_locations]
    face_encodings = []
    try:
        if face_locations:
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            print(f"Found {len(face_encodings)} encodings in frame")
    except Exception as e:
        print("face_encodings error:", e)
        face_encodings = []
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 255), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.imshow('Face Recognition Test', frame)
    if cv2.waitKey(1) == 27:
        break
cap.release()
cv2.destroyAllWindows() 