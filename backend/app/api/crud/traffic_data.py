from typing import List
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models import TrafficData

async def get_all_datas(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100) -> List[TrafficData]:
    collection = db["data_records"]
    cursor = collection.find({}).skip(skip).limit(limit)
    if cursor is None:
        raise HTTPException(status_code=404, detail="No data found")
    return [doc async for doc in cursor]

async def get_data(db: AsyncIOMotorDatabase, device_id:str, skip: int = 0, limit: int = 100) -> TrafficData:
    collection = db["data_records"]
    cursor = collection.find({"device_id": device_id}).skip(skip).limit(limit)
    if cursor is None:
        raise HTTPException(status_code=404, detail="Data not found")

    return [doc async for doc in cursor]