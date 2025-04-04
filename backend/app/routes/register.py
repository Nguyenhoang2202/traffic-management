from fastapi import APIRouter, WebSocket
import json
from app.database import db
from datetime import datetime
router = APIRouter()

@router.websocket("/ws/register")
async def register_camera(websocket: WebSocket):
    await websocket.accept()
    try:
        data = json.loads(await websocket.receive_text())
        camera_id = data.get("camera_id")
        lat = data.get("lat")
        long = data.get("long")

        existing = await db.cameras.find_one({"camera_id": camera_id})
        if not existing:
            await db.cameras.insert_one({
                "camera_id": camera_id,
                "lat": lat,
                "long": long,
                "registered_at": datetime.utcnow()
            })
            print(f"✅ Camera {camera_id} đã đăng ký với vị trí ({lat}, {long})")
        await websocket.send_text("Registration successful")
    except Exception as e:
        print(f"❌ Lỗi đăng ký: {e}")
    finally:
        await websocket.close()
