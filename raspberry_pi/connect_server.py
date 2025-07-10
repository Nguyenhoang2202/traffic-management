import asyncio
import websockets
import json

from camera import Camera
from sensors.rain import RainSensor
from sensors.gps import GPSReader
from devices.traffic_light import traffic_light
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from dotenv import load_dotenv
import os

# Nạp biến môi trường từ .env
load_dotenv()

# Lấy URI
SERVER_URI = os.getenv("SERVER_URI")
async def send_register(ws, device_id, gps: GPSReader):
    
    lat, long = gps.read_coordinates()
    payload = {
        "type": "register",
        "device_id": device_id,
        "gps": {"lat": lat, "long": long}
    }
    await ws.send(json.dumps(payload))
    print("✅ Đã gửi thông tin thiết bị ban đầu")

async def send_data(ws, device_id,camera: Camera, rain_sensor: RainSensor, tlight: traffic_light):
    prev_data = {
        "rain": None,
        "mode": None,
        "auto_mode": None,
        "traffic_light": {
            "state": None,
            "remaining_time": None
        }
    }

    while True:
        try:
            image_data = camera.get_latest_frame()
            payload = {
                "type": "data",
                "device_id": device_id,
                "image": image_data
            }

            rain_status = rain_sensor.get_status()
            auto_mode = tlight.auto_mode
            mode = tlight.mode
            current_data = {
                "rain": rain_status,
                "mode": mode,
                "auto_mode": auto_mode,
                "traffic_light": {
                    "state": tlight.state.state,
                    "remaining_time": tlight.get_remaining_time()
                }
            }
            # XỬ LÝ TỰ ĐỘNG MODE THEO RAIN + AUTO
            # if auto_mode == 1:
            #     mode_reset_once = False  # Cho phép reset lần sau nếu auto_mode bị tắt rồi bật lại
            #     if rain_status and mode != 1:
            #         tlight.mode = 1
            #         print(f"🌧️ Mưa – Chuyển sang mode=1")
            #     elif rain_status and mode != 0:
            #         tlight.mode = 0
            #         print(f"☀️ Không mưa – Chuyển về mode=0")
            # elif auto_mode == 0:
            #     if mode == 1 and not mode_reset_once:
            #         tlight.mode = 0
            #         mode_reset_once = True
            #         print(f"🛑 Người dùng điều khiển – Trả về mode=0 một lần")

            # So sánh và chỉ gửi nếu khác
            for key in ["rain", "mode", "auto_mode"]:
                if current_data[key] != prev_data[key]:
                    payload[key] = current_data[key]
                    prev_data[key] = current_data[key]

            for key in ["state", "remaining_time"]:
                if current_data["traffic_light"][key] != prev_data["traffic_light"][key]:
                    payload.setdefault("traffic_light", {})[key] = current_data["traffic_light"][key]
                    prev_data["traffic_light"][key] = current_data["traffic_light"][key]
            
            payload["datetime"] = datetime.now().isoformat()

            await ws.send(json.dumps(payload))

        except Exception as e:
            print(f"❌ Lỗi gửi dữ liệu: {e}")
            raise e

        await asyncio.sleep(0.041)

class TrafficCommand(BaseModel):            
    mode: Optional[int] = None
    auto_mode: Optional[bool] = None
    green_time: Optional[int] = None
    red_time: Optional[int] = None

async def listen_from_server(ws, tlight: traffic_light):
    while True:
        try:
            message = await ws.recv()
            data = json.loads(message)

            if data["type"] == "command":
                print("received!")
                command = TrafficCommand(**data["data"])

                # Cập nhật trạng thái đèn
                if command.mode is not None:
                    tlight.mode = command.mode
                if command.auto_mode is not None:
                    tlight.auto_mode = command.auto_mode
                if command.green_time is not None:
                    tlight.g.time_on = command.green_time
                if command.red_time is not None:
                    tlight.r.time_on = command.red_time

                print("Command received:", command)

        except Exception as e:
            print(f"❌ Lỗi khi nhận lệnh từ server: {e}")
            break


async def connect_forever(device_id, camera: Camera, rain_sensor: RainSensor, gps: GPSReader, tlight: traffic_light):
    while True:
        try:
            print(f"🔄 Đang cố kết nối tới {SERVER_URI} ...")
            async with websockets.connect(SERVER_URI) as ws:
                print("✅ Kết nối WebSocket thành công!")

                # Gửi đăng ký 1 lần
                await send_register(ws, device_id, gps)

                # Chờ xác nhận từ server
                response = await ws.recv()
                try:
                    response_data = json.loads(response)
                    if response_data.get("type") == "ack" and response_data.get("status") == "ok":
                        print("📩 Server xác nhận đăng ký thành công. Bắt đầu gửi dữ liệu...")
                        send_task = asyncio.create_task(send_data(ws, device_id, camera, rain_sensor, tlight))
                        listen_task = asyncio.create_task(listen_from_server(ws, tlight))

                        # Chờ cả hai task hoàn thành
                        await asyncio.gather(send_task, listen_task)
                                                
                    else:
                        print("❌ Đăng ký thất bại hoặc phản hồi không hợp lệ:", response_data)
                        continue  # Quay lại kết nối lại
                except json.JSONDecodeError:
                    print("❌ Không thể phân tích phản hồi từ server:", response)
                    continue

        except Exception as e:
            print(f"⚠️ Mất kết nối WebSocket: {e}")
            print("⏳ Thử lại sau 5 giây...\n")
            await asyncio.sleep(5)


if __name__ == "__main__":
    print("Chạy file này từ main.py để tích hợp hệ thống.")
