import cv2
import numpy as np

try:
    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
    MEDIAPIPE_OK = True
except Exception as e:
    print(f"[WARNING] eye_movement MediaPipe init failed: {e}")
    MEDIAPIPE_OK = False
    face_mesh = None

LEFT_EYE_LANDMARKS  = [33, 133]
RIGHT_EYE_LANDMARKS = [362, 263]

def get_eye_direction(landmarks, image_width):
    left_eye_x   = landmarks[LEFT_EYE_LANDMARKS[0]].x * image_width
    right_eye_x  = landmarks[RIGHT_EYE_LANDMARKS[1]].x * image_width
    eye_center_x = (left_eye_x + right_eye_x) / 2

    if eye_center_x < image_width * 0.35:
        return "Looking Left"
    elif eye_center_x > image_width * 0.65:
        return "Looking Right"
    else:
        return "Looking Center"

def process_eye_movement(frame):
    if not MEDIAPIPE_OK or face_mesh is None:
        return frame, "Looking Center"

    try:
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results   = face_mesh.process(image_rgb)

        gaze_direction = "Looking Center"

        if results.multi_face_landmarks:
            landmarks      = results.multi_face_landmarks[0].landmark
            h, w, _        = frame.shape
            gaze_direction = get_eye_direction(landmarks, w)

        return frame, gaze_direction

    except Exception as e:
        print(f"[WARNING] eye_movement error: {e}")
        return frame, "Looking Center"