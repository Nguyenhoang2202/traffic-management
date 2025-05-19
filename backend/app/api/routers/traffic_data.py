from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models import TrafficData
from ..crud.traffic_data import *
from ...database.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from ...auth.authorization import *

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
    
@router.get("/export/", response_class=StreamingResponse)
async def export_datas(skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        # Lấy dữ liệu từ CRUD
        datas = await get_all_datas(db=db, skip=skip, limit=limit)

        if not datas:
            raise HTTPException(status_code=404, detail="Không có dữ liệu để xuất")

        # Xử lý DataFrame
        df = pd.DataFrame(datas)

        # Chuyển _id thành chuỗi nếu cần
        if "_id" in df.columns:
            df["_id"] = df["_id"].astype(str)

        # Ghi vào Excel buffer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="TrafficData")
        output.seek(0)

        # Trả về file Excel
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=traffic_data.xlsx"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/export/{camera_id}", response_class=StreamingResponse)
async def export_data(camera_id:str,skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        # Lấy dữ liệu từ CRUD
        datas = await get_data(db=db, device_id=camera_id,skip=skip, limit=limit)

        if not datas:
            raise HTTPException(status_code=404, detail="Không có dữ liệu để xuất")

        # Xử lý DataFrame
        df = pd.DataFrame(datas)

        # Chuyển _id thành chuỗi nếu cần
        if "_id" in df.columns:
            df["_id"] = df["_id"].astype(str)

        # Ghi vào Excel buffer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="TrafficData")
        output.seek(0)

        # Trả về file Excel
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=traffic_data.xlsx"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))