from typing import List
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models import TrafficData
from pymongo import DESCENDING

async def get_all_datas(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100) -> List[TrafficData]:
    collection = db["data_records"]
    cursor = collection.find({}).sort("timestamp", DESCENDING).skip(skip).limit(limit)
    if cursor is None:
        raise HTTPException(status_code=404, detail="No data found")
    data = [doc async for doc in cursor]
    data.reverse()
    return data

async def get_data(db: AsyncIOMotorDatabase, device_id:str, skip: int = 0, limit: int = 100) -> TrafficData:
    collection = db["data_records"]
    cursor = collection.find({"device_id": device_id}).sort("timestamp", DESCENDING).skip(skip).limit(limit)
    if cursor is None:
        raise HTTPException(status_code=404, detail="Data not found")
    data = [doc async for doc in cursor]
    data.reverse()
    return data