import cv2
import numpy as np
import dlib 
import os

detector = dlib.get_frontal_face_detector()
training_data_folder = 'image_folder'
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_recognizer = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")
face_encodings = []
labels = []
for person_name in os.listdir(training_data_folder):
    person_folder = os.path.join(training_data_folder, person_name)
    if os.path.isdir(person_folder):
        person_id = int(person_name.replace('person', ''))  # Extract the person's ID
        for filename in os.listdir(person_folder):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(person_folder, filename)
                image = cv2.imread(image_path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = detector(gray)

                for face in faces:
                    shape = predictor(gray, face)
                    face_encoding = face_recognizer.compute_face_descriptor(image, shape)
                    face_encodings.append(face_encoding)
                    labels.append(person_id)
labels = np.array(labels)
face_encodings = np.array(face_encodings)

print("train")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    print("finish")

    for face in faces:
        shape = predictor(gray, face)
        face_encoding = face_recognizer.compute_face_descriptor(frame, shape)
        distances = np.linalg.norm(face_encodings - face_encoding, axis=1)
        min_distance_idx = np.argmin(distances)
        min_distance = distances[min_distance_idx]
        print(min_distance)

        if min_distance < 0.5:
            label = labels[min_distance_idx]
        else:
            label = "Unknown"

        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f'Person {label}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow('Face Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

