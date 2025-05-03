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
