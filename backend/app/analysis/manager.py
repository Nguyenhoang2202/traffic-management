import json
from app.websocket_routers.device_connecting import connecting_devices
async def send_command_to_device(device_id: str, command_data: dict):
    if device_id in connecting_devices:
        try:
            ws = connecting_devices[device_id]["websocket"]
            await ws.send_text(json.dumps({
                "type": "command",
                "data": command_data
            }))
            print(f"📤 Đã gửi lệnh tới thiết bị {device_id}")
        except Exception as e:
            print(f"❌ Gửi thất bại: {e}")
