import asyncio
from fastapi import FastAPI, WebSocket, APIRouter
import json
import base64
import cv2
from fastapi.websockets import WebSocketState
import numpy as np
from app.websocket_routers.device_connecting import connecting_devices
# from app.testvideo import display_image_from_base64
from app.database.database import save_camera_info

ws_device_router = APIRouter()

@ws_device_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Client đã kết nối")
    is_registered = False
    try:
        while True:
            data = await websocket.receive_text()
            # print("📥 Nhận dữ liệu từ client.")

            try:
                packet = json.loads(data)
            except json.JSONDecodeError:
                print("❌ Không thể giải mã JSON.")
                continue

            msg_type = packet.get("type")

            if not is_registered:
                if msg_type == "register":
                    device_id = packet.get("device_id")
                    gps = packet.get("gps", {})
                    #
                    connecting_devices[device_id] = {
                        "websocket": websocket,
                          "last_data": {},
                          "last_detect_data": {},
                          "last_analyze_data":{}, 
                          "last_predict_data": {},# Test
                          "reset_detect": False, 
                          "reset_analyze": False,
                          "reset_predict": True,# Test
                        }
                    #
                    print(f"Nhận đăng ký từ thiết bị {device_id}, vị trí: {gps}")

                    # Gửi dữ liệu lên DB
                    await save_camera_info(device_id=device_id, latitude=gps["lat"], longitude=gps["long"])
                    
                    # Gửi phản hồi đăng ký thành công
                    ack = {"type": "ack", "status": "ok"}
                    await websocket.send_text(json.dumps(ack))

                    is_registered = True  # Đánh dấu đã đăng ký xong

                else:
                    print("⚠️ Chưa đăng ký mà gửi dữ liệu? Bỏ qua.")
                    continue  # Bỏ qua bất cứ thứ gì khác trước khi đăng ký
            else:
                if msg_type == "data":
                    device_id = packet.get("device_id")
                    traffic_light = packet.get("traffic_light", {})
                    
                    last_data = connecting_devices[device_id]["last_data"]

                    # Cập nhật từng phần nếu có dữ liệu
                    allowed_fields = ["image", "rain", "mode", "auto_mode","timestamp"]

                    for field in allowed_fields:
                        value = packet.get(field)
                        if value is not None:
                            last_data[field] = value

                    if traffic_light is not None:
                        # Nếu trước đó chưa có traffic_light, khởi tạo rỗng
                        if "traffic_light" not in last_data:
                            last_data["traffic_light"] = {}

                        # Cập nhật từng phần của traffic_light nếu có
                        for key in ["state", "remaining_time"]:
                            value = traffic_light.get(key)
                            if value is not None:
                                last_data["traffic_light"][key] = value
# Test video        
                    # display_image_from_base64(image)
                else:
                    print("⚠️ Gói tin không hợp lệ hoặc thiếu type=data.")

    except Exception as e:
        print(f"❌ Lỗi file rpi_connect: {e}")
        cv2.destroyAllWindows()
        # 🧹 Tìm và xóa device_id ra khỏi connecting_devices
        for device_id, info in list(connecting_devices.items()):
            if info["websocket"] == websocket:
                del connecting_devices[device_id]
                print(f"🔌 Đã gỡ thiết bị {device_id} khỏi danh sách kết nối.")
                break


    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
        cv2.destroyAllWindows()
        # 🧹 Tìm và xóa device_id ra khỏi connecting_devices
        for device_id, info in list(connecting_devices.items()):
            if info["websocket"] == websocket:
                del connecting_devices[device_id]
                print(f"🔌 Đã gỡ thiết bị {device_id} khỏi danh sách kết nối.")
                break
        print("🔌 WebSocket đã ngắt kết nối.")

