import asyncio
from fastapi import Query, WebSocket, APIRouter
import json

from fastapi.websockets import WebSocketState
from app.websocket_routers.device_connecting import connecting_devices

ws_fe_router = APIRouter()

@ws_fe_router.websocket("/ws/fe")
async def websocket_fe(websocket: WebSocket,device_id: str = Query(...)):
    await websocket.accept()
    print("🎥 FE đã kết nối để nhận video.")

    try:# hoặc dùng 0 nếu dùng webcam

        while True:
            device = connecting_devices.get(device_id)
            if not device:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Thiết bị '{device_id}' chưa kết nối."
                }))
                await asyncio.sleep(1)
                continue

            last_detect_data = device.get("last_detect_data", {})
            img_detected = last_detect_data.get("img_detected")
            num_current = last_detect_data.get("num_current")
            num_total = last_detect_data.get("num_total")
            cover_ratio = last_detect_data.get("cover_ratio")
            if img_detected:
                await websocket.send_text(json.dumps({
                    "type": "detect",
                    "type": "detect",
                    "img_detected": img_detected,
                    "num_current": num_current,
                    "num_total": num_total,
                    "cover_ratio": cover_ratio
                }))

            await asyncio.sleep(0.04)  # khoảng 25 fps

    except Exception as e:
        print(f"❌ Lỗi WebSocket file rpi_connect: {e}")
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
        print("🔌 Đã đóng kết nối WebSocket /ws/fe")
