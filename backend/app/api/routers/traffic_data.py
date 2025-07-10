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
    

# Spam fake data cho thiết bị
from fastapi import UploadFile, File
from bson import ObjectId

@router.post("/import/")
async def import_traffic_data(file: UploadFile = File(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        # Kiểm tra định dạng
        if not file.filename.endswith(".json"):
            raise HTTPException(status_code=400, detail="Chỉ chấp nhận file JSON")

        # Đọc nội dung file vào DataFrame
        contents = await file.read()
        df = pd.read_json(io.BytesIO(contents), orient="records")

        # Loại bỏ cột _id nếu có (MongoDB sẽ tự tạo)
        if "_id" in df.columns:
            df.drop(columns=["_id"], inplace=True)

        # Chuyển đổi DataFrame thành list dict
        records = df.to_dict(orient="records")

        if not records:
            raise HTTPException(status_code=400, detail="Không có bản ghi nào trong file")

        # Gọi CRUD để insert
        from ..crud.traffic_data import insert_many_traffic_data
        result = await insert_many_traffic_data(db=db, data_list=records)

        return {"message": "Import thành công", "inserted_count": len(result.inserted_ids)}

    except ValueError:
        raise HTTPException(status_code=400, detail="Định dạng JSON không hợp lệ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/count/count_datas")
async def count_datas(db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        count = await db["traffic_data"].count_documents({})
        return {"total_documents": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/datas/clear_all")
async def clear_all_traffic_data(db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        result = await db["traffic_data"].delete_many({})
        return {
            "message": "Đã xóa toàn bộ dữ liệu",
            "deleted_count": result.deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))