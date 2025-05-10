import asyncio
import re
from fastapi import Query, WebSocket, APIRouter
import json

from fastapi.websockets import WebSocketState
from app.websocket_routers.device_connecting import connecting_devices
from urllib.parse import parse_qs

ws_fe_router = APIRouter()

# Hàm tách số từ device_id (ví dụ: "C10" -> 10)
def extract_number(device_id):
    match = re.search(r'\d+', device_id)
    return int(match.group()) if match else float('inf')

@ws_fe_router.websocket("/ws/fe")
async def websocket_fe(websocket: WebSocket):
    await websocket.accept()
    print("🎥 FE đã kết nối để nhận video.")

    try:
        query_params = parse_qs(websocket.url.query)
        page = int(query_params.get("page", [1])[0])
        page_size = int(query_params.get("page_size", [4])[0])
    except (ValueError, TypeError):
        page = 1
        page_size = 4   # Giá trị mặc định nếu không có hoặc không hợp lệ
        

    try:
        while True:
            # Sắp xếp danh sách theo thứ tự tên device (theo số)
            sorted_devices = sorted(connecting_devices.items(), key=lambda x: extract_number(x[0]))

            # Phân trang
            start = (page - 1) * page_size
            end = start + page_size
            paged_devices = sorted_devices[start:end]

            data_to_send = []

            for device_id, device in paged_devices:
                last_detect_data = device.get("last_detect_data", {})
                img_detected = last_detect_data.get("img_detected")
                num_current = last_detect_data.get("num_current")
                num_total = last_detect_data.get("num_total")
                cover_ratio = last_detect_data.get("cover_ratio")

                if img_detected:
                    data_to_send.append({
                        "device_id": device_id,
                        "img_detected": img_detected,
                        "num_current": num_current,
                        "num_total": num_total,
                        "cover_ratio": cover_ratio
                    })

            await websocket.send_text(json.dumps({
                "type": "batch_detect",
                "data": data_to_send
            }))

            await asyncio.sleep(0.04)  # khoảng 25 fps

    except Exception as e:
        print(f"❌ Lỗi WebSocket file rpi_connect: {e}")
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
        print("🔌 Đã đóng kết nối WebSocket /ws/fe")
