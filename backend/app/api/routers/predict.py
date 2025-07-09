from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models import PredictData
from ..crud.predict import *
from ...database.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...auth.authorization import *

router = APIRouter(prefix="/predicts", tags=["predicts"])

@router.get("/", response_model=List[PredictData])
async def read_predict_datas(skip:int= 0,limit:int=100,db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        return await get_all_predict_datas(db=db,skip=skip,limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{camera_id}", response_model=List[PredictData])
async def read_predict_data(camera_id: str,skip:int= 0,limit:int=100, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        return await get_predict_data(db=db, device_id=camera_id,skip=skip,limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
