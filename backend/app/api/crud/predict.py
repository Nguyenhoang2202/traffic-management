from typing import List
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models import PredictData
from ...auth.authentication import hash_password,verify_password, create_access_token
from pymongo import DESCENDING

async def get_all_predict_datas(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100) -> List[PredictData]:
    collection = db["predict_traffic"]
    cursor = collection.find({}).sort("create_time", DESCENDING).skip(skip).limit(limit)
    if cursor is None:
        raise HTTPException(status_code=404, detail="No data found")
    data = [doc async for doc in cursor]
    data.reverse()
    return data

async def get_predict_data(db: AsyncIOMotorDatabase, device_id:str, skip: int = 0, limit: int = 100) -> PredictData:
    collection = db["predict_traffic"]
    cursor = collection.find({"device_id": device_id}).sort("create_time", DESCENDING).skip(skip).limit(limit)
    if cursor is None:
        raise HTTPException(status_code=404, detail="Data not found")
    data = [doc async for doc in cursor]
    data.reverse()
    return data