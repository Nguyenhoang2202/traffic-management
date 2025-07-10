from typing import List
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models import Camera

async def get_all_cameras(db: AsyncIOMotorDatabase) -> List[Camera]:
    collection = db["Cameras"]
    cursor = collection.find({})
    if cursor is None:
        raise HTTPException(status_code=404, detail="No cameras found")
    return [doc async for doc in cursor]

async def get_camera(db: AsyncIOMotorDatabase, device_id:str) -> Camera:
    collection = db["Cameras"]
    camera = await collection.find_one({"device_id": device_id})
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")

    return camera