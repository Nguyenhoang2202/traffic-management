from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models import Camera
from ..crud.camera import *
from ...database.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/cameras", tags=["cameras"])

@router.get("/", response_model=List[Camera])
async def read_cameras(db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        return await get_all_cameras(db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{camera_id}", response_model=Camera)
async def read_camera(camera_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        return await get_camera(db=db, device_id=camera_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))