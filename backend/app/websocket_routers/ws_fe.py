import asyncio
from fastapi import WebSocket, APIRouter
import json

from fastapi.websockets import WebSocketState
from app.websocket_routers.device_connecting import connecting_devices

ws_fe_router = APIRouter()

@ws_fe_router.websocket("/ws/fe")
async def websocket_fe(websocket: WebSocket):
    await websocket.accept()
    print("🎥 FE đã kết nối để nhận video.")

    try:# hoặc dùng 0 nếu dùng webcam

        while True:
            base64_str = connecting_devices["C1"]["last_detect_data"]["img_detected"]

            # Gửi frame qua WebSocket
            await websocket.send_text(json.dumps({
                "type": "frame",
                "data": base64_str
            }))

            await asyncio.sleep(0.04)  # khoảng 25 fps

    except Exception as e:
        print(f"❌ Lỗi WebSocket file rpi_connect: {e}")
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
        print("🔌 Đã đóng kết nối WebSocket /ws/fe")
