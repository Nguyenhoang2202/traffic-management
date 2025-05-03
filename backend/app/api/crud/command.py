import json
from ...websocket_routers.device_connecting import connecting_devices
from typing import List
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models import Command
from fastapi.encoders import jsonable_encoder

async def send_command_to_device(device_id: str, command_data: dict):
    """
    Gửi lệnh đến thiết bị qua WebSocket.
    """
    if device_id in connecting_devices:
        try:
            ws = connecting_devices[device_id]["websocket"]

            safe_command_data = jsonable_encoder(command_data)
            
            print(safe_command_data)
            await ws.send_text(json.dumps({
                "type": "command",
                "data": safe_command_data
            }))
            print(f"📤 Đã gửi lệnh tới thiết bị {device_id}")
        except Exception as e:
            raise Exception(f"❌ Gửi thất bại: {e}")
    else:
        raise ValueError(f"Thiết bị {device_id} không tồn tại trong danh sách kết nối.")
    
async def create_command(db: AsyncIOMotorDatabase, command: Command):
    collection = db["commands"]
    new_command = command.model_dump(by_alias=True)
    await send_command_to_device(new_command["device_id"],command_data=new_command)
    await collection.insert_one(new_command)
    return new_command

async def get_all_commands(db: AsyncIOMotorDatabase,skip:int=0,limit:int=100):
    collection = db["commands"]
    cursor = collection.find().skip(skip).limit(limit)
    if cursor is None:
        raise HTTPException(status_code=404, detail="No commend found")
    return [doc async for doc in cursor]

async def get_user_commands(db: AsyncIOMotorDatabase, user_id: str,skip:int=0,limit:int=100):
    collection = db["commands"]
    cursor = collection.find({"user_id": user_id}).skip(skip).limit(limit)
    if cursor is None:
        raise HTTPException(status_code=404, detail="No commend found")
    return [doc async for doc in cursor]