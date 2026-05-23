import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import math

try:
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
    MEDIAPIPE_OK = True
except Exception as e:
    print(f"[WARNING] MediaPipe init failed: {e}")
    MEDIAPIPE_OK = False
    face_mesh = None

# Camera Calibration (Assuming 640x480)
focal_length = 640
center = (320, 240)
camera_matrix = np.array([
    [focal_length, 0, center[0]],
    [0, focal_length, center[1]],
    [0, 0, 1]
], dtype=np.float64)
dist_coeffs = np.zeros((4, 1))

ANGLE_HISTORY_SIZE = 10
yaw_history = deque(maxlen=ANGLE_HISTORY_SIZE)
pitch_history = deque(maxlen=ANGLE_HISTORY_SIZE)
roll_history = deque(maxlen=ANGLE_HISTORY_SIZE)

previous_state = "Looking at Screen"

# Facial landmark indices (Mediapipe)
landmark_indices = {
    "nose_tip": 1,
    "chin": 152,
    "left_eye": 263,
    "right_eye": 33,
    "left_mouth": 61,
    "right_mouth": 291
}

model_points = np.array([
    (0.0, 0.0, 0.0),        # Nose tip
    (0.0, -50.0, -10.0),    # Chin
    (-30.0, 40.0, -10.0),   # Left eye
    (30.0, 40.0, -10.0),    # Right eye
    (-25.0, -30.0, -10.0),  # Left mouth corner
    (25.0, -30.0, -10.0)    # Right mouth corner
], dtype=np.float64)

def get_head_pose_angles(image_points):
    success, rotation_vector, translation_vector = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    if not success:
        return None

    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    sy = math.sqrt(rotation_matrix[0, 0]**2 + rotation_matrix[1, 0]**2)
    singular = sy < 1e-6

    if not singular:
        pitch = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        yaw = math.atan2(-rotation_matrix[2, 0], sy)
        roll = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    else:
        pitch = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
        yaw = math.atan2(-rotation_matrix[2, 0], sy)
        roll = 0

    return np.degrees(pitch), np.degrees(yaw), np.degrees(roll)

def smooth_angle(angle_history, new_angle):
    angle_history.append(new_angle)
    return np.mean(angle_history)

def process_head_pose(frame, calibrated_angles=None):
    global previous_state
    head_direction = "No Face Detected"

    if not MEDIAPIPE_OK or face_mesh is None:
        return frame, head_direction

    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            h, w, _ = frame.shape

            image_points = np.array([
                (landmarks.landmark[landmark_indices["nose_tip"]].x * w, landmarks.landmark[landmark_indices["nose_tip"]].y * h),
                (landmarks.landmark[landmark_indices["chin"]].x * w, landmarks.landmark[landmark_indices["chin"]].y * h),
                (landmarks.landmark[landmark_indices["left_eye"]].x * w, landmarks.landmark[landmark_indices["left_eye"]].y * h),
                (landmarks.landmark[landmark_indices["right_eye"]].x * w, landmarks.landmark[landmark_indices["right_eye"]].y * h),
                (landmarks.landmark[landmark_indices["left_mouth"]].x * w, landmarks.landmark[landmark_indices["left_mouth"]].y * h),
                (landmarks.landmark[landmark_indices["right_mouth"]].x * w, landmarks.landmark[landmark_indices["right_mouth"]].y * h)
            ], dtype=np.float64)

            angles = get_head_pose_angles(image_points)
            if angles is None:
                return frame, head_direction

            pitch = smooth_angle(pitch_history, angles[0])
            yaw   = smooth_angle(yaw_history,   angles[1])
            roll  = smooth_angle(roll_history,   angles[2])

            if calibrated_angles is None:
                return frame, (pitch, yaw, roll)

            pitch_offset, yaw_offset, roll_offset = calibrated_angles
            PITCH_THRESHOLD = 8
            YAW_THRESHOLD   = 12
            ROLL_THRESHOLD  = 5

            if abs(yaw - yaw_offset) <= YAW_THRESHOLD and abs(pitch - pitch_offset) <= PITCH_THRESHOLD and abs(roll - roll_offset) <= ROLL_THRESHOLD:
                current_state = "Looking at Screen"
            elif yaw < yaw_offset - 15:
                current_state = "Looking Left"
            elif yaw > yaw_offset + 15:
                current_state = "Looking Right"
            elif pitch > pitch_offset + 10:
                current_state = "Looking Up"
            elif pitch < pitch_offset - 10:
                current_state = "Looking Down"
            elif abs(roll - roll_offset) > 7:
                current_state = "Tilted"
            else:
                current_state = previous_state

            previous_state = current_state
            head_direction = current_state

    except Exception as e:
        print(f"[WARNING] head_pose error: {e}")

  

    return frame, head_direction

