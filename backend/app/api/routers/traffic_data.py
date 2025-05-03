from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models import TrafficData
from ..crud.traffic_data import *
from ...database.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/datas", tags=["datas"])

@router.get("/", response_model=List[TrafficData])
async def read_cameras(skip:int= 0,limit:int=100,db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        return await get_all_datas(db=db,skip=skip,limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{camera_id}", response_model=List[TrafficData])
async def read_camera(camera_id: str,skip:int= 0,limit:int=100, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        return await get_data(db=db, device_id=camera_id,skip=skip,limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))