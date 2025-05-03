import cv2
import numpy as np
from ultralytics import YOLO
from app.sort import Sort
import torch
import torchvision

print(f"Torch: {torch.__version__}, TorchVision: {torchvision.__version__}")

VALID_CLASSES = {"car", "truck", "bus", "motorbike", "motorcycle"}

model = YOLO("yolov8m.pt")
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

# Hàm chọn ROI
def select_roi(cap):
    roi_points = []

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(roi_points) < 4:
            roi_points.append((x, y))

    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Failed to read first frame for ROI selection")

    cv2.namedWindow("Select Quadrilateral ROI")
    cv2.setMouseCallback("Select Quadrilateral ROI", mouse_callback)

    while True:
        temp_frame = frame.copy()
        for pt in roi_points:
            cv2.circle(temp_frame, pt, 5, (0, 0, 255), -1)
        if len(roi_points) == 4:
            cv2.polylines(temp_frame, [np.array(roi_points)], isClosed=True, color=(255, 0, 0), thickness=2)
        cv2.imshow("Select Quadrilateral ROI", temp_frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or len(roi_points) == 4:
            break

    cv2.destroyWindow("Select Quadrilateral ROI")
    return np.array(roi_points), frame

# Hàm kiểm tra đối tượng có nằm trong vùng không
def is_inside_roi(x_center, y_center, roi_polygon):
    return cv2.pointPolygonTest(roi_polygon, (x_center, y_center), False) >= 0

# VIDEO_SOURCE= "app/detect/highway.mp4"
def analyze_video_stream(video_source="app/detect/q.mp4"):
    # 
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open source: {video_source}")
    
    roi_polygon, frame = select_roi(cap)# Gọi hàm lấy polygon vẽ mark
    print("Selected ROI Points:", roi_polygon.tolist())

    # Khởi tạo lại video
    if isinstance(video_source, str):# Kiểm tra nếu video đưa vào là 1 chuỗi thì nó là video
        cap.release()# Giải phóng video đang mở
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise RuntimeError("Cannot reopen video after ROI selection")

    # Tạo mark cho ROI
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)# tạo full nền đen cùng kích thước
    cv2.fillPoly(mask, [roi_polygon], 255)# điền trắng phần ROI

    x_offset, y_offset, w_mask, h_mask = cv2.boundingRect(roi_polygon)# Lấy hình vuông bao bên ngoài

    current_ids = set()
    crossed_ids = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.polylines(frame, [roi_polygon], isClosed=True, color=(255, 0, 0), thickness=2)

        # Đè mark vào frame
        masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

        # Cắt Roi ra khỏi frame chỉ để phần nhỏ lại để phân tích 
        roi_crop = masked_frame[y_offset:y_offset + h_mask, x_offset:x_offset + w_mask]
        if roi_crop.size == 0:
            continue

        rgb_roi = cv2.cvtColor(roi_crop, cv2.COLOR_BGR2RGB)
        results = model(rgb_roi, verbose=False)[0]

        dets = []# Các đối tượng được phát hiện
        for det in results.boxes:
            x1, y1, x2, y2 = map(int, det.xyxy[0].tolist())
            conf = float(det.conf[0])
            cls_id = int(det.cls[0])
            label = model.names[cls_id]

            if conf < 0.4 or label not in VALID_CLASSES:
                continue

            x_center = x1 + (x2 - x1) // 2 + x_offset
            y_center = y1 + (y2 - y1) // 2 + y_offset
            if not is_inside_roi(x_center, y_center, roi_polygon):
                continue

            dets.append([x1 + x_offset, y1 + y_offset, x2 + x_offset, y2 + y_offset, conf])

        # dets là danh sách các detection từ YOLO đã qua lọc
        dets_np = np.array(dets) if dets else np.empty((0, 5))
        tracks = tracker.update(dets_np)

        #
        for *bbox, track_id in tracks.astype(int):
            x1, y1, x2, y2 = bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID:{track_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            current_ids.add(track_id)
            if track_id not in crossed_ids:
                crossed_ids.add(track_id)

        num_current = len(current_ids)
        num_total = len(crossed_ids)

        cv2.putText(frame, f"Current: {num_current}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Total: {num_total}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        current_ids.clear()

        cv2.imshow("YOLOv8 + SORT Tracking with ROI", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return {
        "roi_points": roi_polygon.tolist(),
        "total_vehicles": len(crossed_ids)
    }

if __name__ == "__main__":
    stats = analyze_video_stream()
    print("Session stats:", stats)
