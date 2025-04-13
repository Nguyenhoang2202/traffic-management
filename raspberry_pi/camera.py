import asyncio
import websockets
import base64
import cv2
from picamera2 import Picamera2

SERVER_URI = "ws://192.168.0.105:8222/ws"

class Camera:
    def __init__(self, resolution=(640, 480)):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": resolution}))
        self.picam2.start()
        self.latest_frame = None
        self.running = True

    async def run(self):
        while self.running:
            frame = self.picam2.capture_array()
            if frame is not None:
                _, buffer = cv2.imencode(".jpg", frame)
                self.latest_frame = base64.b64encode(buffer).decode("utf-8")
            await asyncio.sleep(0.03)

    def get_latest_frame(self):
        return self.latest_frame


# async def connect_forever():
#     picam2 = Picamera2()
#     picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
#     picam2.start()

#     while True:
#         try:
#             print(f"🔄 Đang cố kết nối tới {SERVER_URI} ...")
#             async with websockets.connect(SERVER_URI) as ws:
#                 print("✅ Kết nối WebSocket thành công!")
#                 await send_video(ws, picam2)

#         except Exception as e:
#             print(f"⚠️ Mất kết nối WebSocket: {e}")
#             print("⏳ Thử lại sau 5 giây...\n")
#             await asyncio.sleep(5)

# if __name__ == "__main__":
#     try:
#         asyncio.run(connect_forever())
#     except KeyboardInterrupt:
#         print("🛑 Đã dừng client theo yêu cầu.")
