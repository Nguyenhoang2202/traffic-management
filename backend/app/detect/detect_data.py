import asyncio
import base64
import math
import time
import cv2
from app.websocket_routers.device_connecting import connecting_devices,get_frame_from_device
import numpy as np
from ultralytics import YOLO
from app.sort import Sort
import torch
import torchvision

print(f"Torch: {torch.__version__}, TorchVision: {torchvision.__version__}")

VALID_CLASSES = {"car", "truck", "bus", "motorbike", "motorcycle"}

model = YOLO("yolov8m.pt") 

#-----------------------------------------------------
# Hàm chọn ROI
def select_roi(frame):
    roi_points = [[107, 64], [102, 440], [562, 434], [569, 59]]

    # def mouse_callback(event, x, y, flags, param):
    #     if event == cv2.EVENT_LBUTTONDOWN and len(roi_points) < 4:
    #         roi_points.append((x, y))

    # cv2.namedWindow("Select Quadrilateral ROI")
    # cv2.setMouseCallback("Select Quadrilateral ROI", mouse_callback)

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
    return  np.array(roi_points), frame

#-----------------------------------------------------
# # Hàm tính độ rộng của đoạn đường
# def get_road_width(roi_polygon: np.ndarray) -> float:
#     # 
#     sorted_points = sorted(roi_polygon, key=lambda pt: pt[1], reverse=True) # Sắp xếp từ lớn tới bé theo y
#     bottom_points = sorted_points[:2]  # lấy 2 điểm thấp nhất (ở đầu)

#     # Tìm 2 điểm xa nhau nhất trong số các điểm đáy
#     (x1, y1), (x2, y2) = bottom_points
#     width = math.hypot(x2 - x1, y2 - y1)

#     return width 

#-----------------------------------------------------
# Hàm tính độ che phủ
def calculate_weighted_cover_ratio(vehicles_in_roi_mask: np.ndarray,roi_only_mask: np.ndarray) -> float:
    h, _ = vehicles_in_roi_mask.shape
    total_weight = 0
    cover_weight = 0

    for y in range(h):
        row_weight = (h - y) / h  # y càng nhỏ → trọng số càng cao
        total_weight += row_weight * np.sum(roi_only_mask[y, :] > 0)
        cover_weight += row_weight * np.sum(vehicles_in_roi_mask[y, :] > 0)

    return cover_weight / total_weight if total_weight > 0 else 0.0

#-----------------------------------------------------
# Hàm kiểm tra đối tượng có nằm trong vùng không
def is_inside_roi(x_center, y_center, roi_polygon):
    return cv2.pointPolygonTest(roi_polygon, (x_center, y_center), False) >= 0

#-----------------------------------------------------
async def object_detection(device_id):
    # Khởi tạo tracker SORT
    # max_age: số frame tối đa mà một đối tượng có thể không được phát hiện trước khi bị xóa khỏi tracker
    tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

    firstFrame = get_frame_from_device(device_id=device_id)
    
    roi_polygon, frame = select_roi(firstFrame)# Gọi hàm lấy polygon vẽ mark
    print("Selected ROI Points:", roi_polygon.tolist())

    # Lấy chiều rộng của đường
    # road_width = get_road_width(roi_polygon=roi_polygon)
    # connecting_devices[device_id]["last_detect_data"]["road_width"] = road_width

    # Tạo mark cho ROI
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)# tạo full nền đen cùng kích thước
    cv2.fillPoly(mask, [roi_polygon], 255)# điền trắng phần ROI

    # Lấy hình vuông bao bên ngoài ROI
    x_offset, y_offset, w_mask, h_mask = cv2.boundingRect(roi_polygon)
    current_ids = set()
    crossed_ids = set()


    while True:
        # Check reset_detect
        if connecting_devices[device_id]["reset_detect"]:
            tracker.reset()
            connecting_devices[device_id]["reset_detect"] = False
            print(f"Đã reset_detect tracker cho thiết bị {device_id}")

        start_time = time.time()
        try:
            frame = get_frame_from_device(device_id=device_id)
            if frame is None or frame.size == 0:
                await asyncio.sleep(0.1)
                continue

            # Đè mark vào frame
            masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
            # Cắt Roi ra khỏi frame chỉ để phần nhỏ lại để phân tích 
            roi_crop = masked_frame[y_offset:y_offset + h_mask, x_offset:x_offset + w_mask]
            if roi_crop.size == 0:
                continue
            rgb_roi = cv2.cvtColor(roi_crop, cv2.COLOR_BGR2RGB)# Chuyển lại màu

            # Detect bằng YOLOv8
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

            # Tạo mask mới cho vùng phương tiện #DTCP
            vehicles_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    
            for *bbox, track_id in tracks.astype(int):
                x1, y1, x2, y2 = bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"ID:{track_id}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                current_ids.add(track_id)
                if track_id not in crossed_ids:
                    crossed_ids.add(track_id)

                # Vẽ vùng phương tiện lên mask #DTCP
                cv2.rectangle(vehicles_mask, (x1, y1), (x2, y2), 255, -1)
            
            # Tạo mask chỉ giữ lại phần nằm trong ROI #DTCP # Phần ROI
            roi_only_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            cv2.fillPoly(roi_only_mask, [roi_polygon], 255)

            # Lọc phần mask xe nằm trong ROI #DTCP # Phần xe nằm trong ROI
            vehicles_in_roi_mask = cv2.bitwise_and(vehicles_mask, vehicles_mask, mask=roi_only_mask)

            # Tính diện tích che phủ #DTCP
            cover_ratio = calculate_weighted_cover_ratio(vehicles_in_roi_mask,roi_only_mask)

            # Đếm số xe hiện tại và số xe đã đi qua
            num_current = len(current_ids)
            num_total = len(crossed_ids)
            current_ids.clear()

            # In và hiển thị kết quả
            cv2.polylines(frame, [roi_polygon], isClosed=True, color=(0, 0, 255), thickness=2)
            cv2.putText(frame, f"Current: {num_current}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Total: {num_total}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Cover: {cover_ratio:.2f}%", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 100), 2)
            
            if frame is not None:
                _, buffer = cv2.imencode(".jpg", frame)
                img_detected = base64.b64encode(buffer).decode("utf-8")
            
            #
            # print(f"ID: {device_id}, Current: {num_current}, Total: {num_total}, Cover: {cover_ratio:.2f}%")
            last_detect_data = connecting_devices[device_id]["last_detect_data"]
            last_detect_data["img_detected"]=img_detected
            last_detect_data["num_current"]=num_current
            last_detect_data["num_total"]=num_total
            last_detect_data["cover_ratio"]=cover_ratio
            # print(last_detect_data)

            # Cho phép các task async khác chạy
            elapsed = time.time() - start_time
            delay = max(0, (1 / 30) - elapsed)  # Trường hợp elapsed > 1/30 thì delay = 0
            # Đảm bảo delay không quá nhỏ (ví dụ 0.001s)
            delay = max(0.001, delay)  # Dùng 0.001 giây là mức delay nhỏ nhất
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"❌ Lỗi file detect_data: {e}")
            await asyncio.sleep(0.5)

detecting_tasks = dict()  # device_id -> asyncio.Task

async def run_all_detect_tasks_forever():
    while True:
        # Tạo task mới nếu thiết bị mới kết nối
        for device_id in connecting_devices:
            if device_id not in detecting_tasks:
                print("----------------Đã có ID----------------")
                task = asyncio.create_task(object_detection(device_id))
                detecting_tasks[device_id] = task
                print(f"✅ Đã tạo task NHẬN DIỆN cho: {device_id}")

        # Hủy task nếu thiết bị đã mất kết nối
        disconnected_ids = [did for did in detecting_tasks if did not in connecting_devices]
        for did in disconnected_ids:
            task = detecting_tasks.pop(did)
            if not task.done():
                task.cancel()
                print(f"⚠️ Đã hủy task phân tích cho thiết bị {did} do mất kết nối")

        await asyncio.sleep(2)
