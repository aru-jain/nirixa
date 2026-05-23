from ultralytics import YOLO
import cv2

# Load pretrained YOLOv8 model (YOLOv8n is small and fast)
model = YOLO('yolov8n.pt')  # You can also use yolov8s.pt, yolov8m.pt etc.

def process_mobile_detection(frame):
    results = model(frame, verbose=False)[0]
    
    # Check if any class detected is mobile phone (assuming 'mobile phone' was trained)
    mobile_detected = False
    for result in results.boxes:
        class_id = int(result.cls[0])
        class_name = model.names[class_id]
        if class_name.lower() in ['cell phone', 'mobile phone', 'phone']:
            mobile_detected = True
            break
    
    return frame, mobile_detected
