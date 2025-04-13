import asyncio
import websockets
import json

from camera import Camera
from sensors.rain import RainSensor
from sensors.gps import GPSReader
from devices.traffic_light import traffic_light

from dotenv import load_dotenv
import os

# Nạp biến môi trường từ .env
load_dotenv()

# Lấy URI
SERVER_URI = os.getenv("SERVER_URI")
async def send_register(ws, device_id, gps: GPSReader):
    
    lat, lon = gps.read_coordinates()
    payload = {
        "type": "register",
        "device_id": device_id,
        "gps": {"lat": lat, "lon": lon}
    }
    await ws.send(json.dumps(payload))
    print("✅ Đã gửi thông tin thiết bị ban đầu")

async def send_data(ws, device_id,camera: Camera, rain_sensor: RainSensor, tlight: traffic_light):
    prev_rain = None
    prev_mode = None
    prev_auto_mode = None
    prev_traffic_state = None
    prev_remaining_time = None
    while True:
        try:
            image_data = camera.get_latest_frame()
            payload = {
                "type": "data",
                "device_id": device_id,
                "image": image_data
            }
            rain_status = rain_sensor.get_status()
            traffic_mode = tlight.mode
            traffic_auto_mode = tlight.auto_mode
            traffic_state = tlight.state.state
            remaining_time = tlight.get_remaining_time()

            # So sánh và thêm vào payload nếu có thay đổi
            if rain_status != prev_rain:
                payload["rain"] = rain_status
                prev_rain = rain_status

            if traffic_mode != prev_mode:
                payload["mode"] = traffic_mode
                prev_mode = traffic_mode

            if traffic_auto_mode != prev_auto_mode:
                payload["auto_mode"] = traffic_auto_mode
                prev_auto_mode = traffic_auto_mode

            if traffic_state != prev_traffic_state:
                payload.setdefault("traffic_light", {})["state"] = traffic_state
                prev_traffic_state = traffic_state

            if remaining_time != prev_remaining_time:
                payload.setdefault("traffic_light", {})["remaining_time"] = remaining_time
                prev_remaining_time = remaining_time

            await ws.send(json.dumps(payload))
        except Exception as e:
            print(f"❌ Lỗi gửi dữ liệu: {e}")
            raise e
        await asyncio.sleep(0.041)


async def listen_from_server(ws, tlight: traffic_light):
    while True:
        try:
            message = await ws.recv()
            data = json.loads(message)

            if data["type"] == "command":
                print("received!")
                mode = data.get("mode")
                auto_mode = data.get("auto_mode")
                green_time = data.get("data").get("green_time")
                red_time = data.get("red_time")
                print(data)
                
                print(green_time)
                if mode is not None:
                    tlight.mode = mode
                if auto_mode is not None:
                    tlight.auto_mode = auto_mode
                if green_time is not None:
                    tlight.g.time_on = green_time
                if red_time is not None:
                    tlight.r.time_on = red_time

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
