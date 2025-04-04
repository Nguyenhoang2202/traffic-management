from fastapi import APIRouter, WebSocket
import json
from datetime import datetime
from app.database import db

router = APIRouter()

@router.websocket("/ws/stream")
async def stream_data(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = json.loads(await websocket.receive_text())
            camera_id = data["camera_id"]
            sensor_data = data["sensor_data"]
            frame_data = data.get("frame")

            await db.camera_data.insert_one({
                "camera_id": camera_id,
                "timestamp": datetime.utcnow(),
                "frame": frame_data,
                "sensor_data": sensor_data
            })
    except Exception as e:
        print(f"❌ Lỗi streaming: {e}")
    finally:
        await websocket.close()
