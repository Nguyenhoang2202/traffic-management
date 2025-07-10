import json

from bson import ObjectId
from ...websocket_routers.device_connecting import connecting_devices
from typing import List
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models import Command
from fastapi.encoders import jsonable_encoder
from pymongo import DESCENDING

async def send_command_to_device(device_id: str, command_data: dict):
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
    await send_command_to_device(device_id=new_command["device_id"],command_data=new_command)
    await collection.insert_one(new_command)
    return new_command

# async def get_all_commands(db: AsyncIOMotorDatabase,skip:int=0,limit:int=100):
#     collection = db["commands"]
#     cursor = collection.find().sort("timestamp", DESCENDING).skip(skip).limit(limit)
#     if cursor is None:
#         raise HTTPException(status_code=404, detail="No commend found")
#     data = [doc async for doc in cursor]
#     data.reverse()
#     return data


async def get_all_commands(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100):
    command_collection = db["commands"]
    user_collection = db["users"]

    commands_cursor = command_collection.find().sort("timestamp", DESCENDING).skip(skip).limit(limit)
    commands = [doc async for doc in commands_cursor]

    # Lấy tất cả user_id khác nhau
    user_ids = list(set(cmd["user_id"] for cmd in commands if "user_id" in cmd))

    # Truy vấn tất cả user 1 lần
    users_cursor = user_collection.find({"_id": {"$in": [ObjectId(uid) for uid in user_ids]}})
    users = [doc async for doc in users_cursor]

    # Tạo map user_id -> username
    user_map = {str(user["_id"]): user["username"] for user in users}

    # Gắn username vào mỗi command
    for cmd in commands:
        cmd["username"] = user_map.get(cmd["user_id"], "Unknown")

    return commands


async def get_user_commands(db: AsyncIOMotorDatabase, user_id: str,skip:int=0,limit:int=100):
    command_collection = db["commands"]
    user_collection = db["users"]

    commands_cursor = command_collection.find({"user_id":user_id}).sort("timestamp", DESCENDING).skip(skip).limit(limit)
    commands = [doc async for doc in commands_cursor]

    # Lấy tất cả user_id khác nhau
    user_ids = list(set(cmd["user_id"] for cmd in commands if "user_id" in cmd))

    # Truy vấn tất cả user 1 lần
    users_cursor = user_collection.find({"_id": {"$in": [ObjectId(uid) for uid in user_ids]}})
    users = [doc async for doc in users_cursor]

    # Tạo map user_id -> username
    user_map = {str(user["_id"]): user["username"] for user in users}

    # Gắn username vào mỗi command
    for cmd in commands:
        cmd["username"] = user_map.get(cmd["user_id"], "Unknown")

    return commands