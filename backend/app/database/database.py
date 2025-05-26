import asyncio
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from ..websocket_routers.device_connecting import connecting_devices

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Không thay đổi gì ngoài hàm get_db
async def get_db():
    return db

# ====== CÁC COLLECTION ======
data_cameras = db["Cameras"]
data_analyzed = db["data_records"] 

# HÀM GỬI DỮ LIỆU CAMERA LÊN DB
async def save_camera_info(device_id: str, latitude: float, longitude: float):
    camera_info = {
        "device_id": device_id,
        "latitude": latitude,
        "longitude": longitude,
    }
    await data_cameras.update_one(
        {"device_id": device_id},    # Điều kiện tìm kiếm
        {"$set": camera_info},        # Nếu có thì cập nhật theo camera_info
        upsert=True                  # Nếu không có thì tạo mới
    )
    print(f"✅ Đã cập nhật hoặc thêm mới camera: {camera_info}")

# ====== HÀM GỬI DỮ LIỆU LÊN DB ======
async def send_data(device_id: str):
    last_data = connecting_devices[device_id]["last_data"]
    last_detect_data = connecting_devices[device_id]["last_detect_data"]
    last_analyze_data = connecting_devices[device_id]["last_analyze_data"]
    # Các trường dữ liệu sẽ gửi
    data_fields = ["rain", "mode", "auto_mode","timestamp"]
    detect_data_fields = ["num_total"]
    analyze_data_fields = ["all_green_time","numb_turn_green","average_green_time"]

    # Kiểm tra đủ trường trong từng nhóm dữ liệu
    if not all(field in last_data for field in data_fields):
        print("⚠️ Dữ liệu `last_data` chưa đầy đủ.")
        return
    if not all(field in last_detect_data for field in detect_data_fields):
        print("⚠️ Dữ liệu `last_detect_data` chưa đầy đủ.")
        return
    if not all(field in last_analyze_data for field in analyze_data_fields):
        print("⚠️ Dữ liệu `last_analyze_data` chưa đầy đủ.")
        return
    
    # Lấy các dữ liệu tương ứng
    data = {field: last_data[field] for field in data_fields if field in last_data}
    detect_data = {field: last_detect_data[field] for field in detect_data_fields if field in last_detect_data}
    analyze_data = {field: last_analyze_data[field] for field in analyze_data_fields if field in last_analyze_data}
    # Tổng hợp dữ liệu
    data_total = {"device_id":device_id,**data, **detect_data, **analyze_data}
    await data_analyzed.insert_one(data_total)

    # Reset lại dữ liệu sau khi đã gửi lên DB
    connecting_devices[device_id]["reset_detect"] = True
    connecting_devices[device_id]["reset_analyze"] = True
    connecting_devices[device_id]["reset_predict"] = True #Test

    # print(f"✅ Đã lưu dữ liệu lên DB: {data}")

# ====== HÀM TỰ ĐỘNG GỬI DỮ LIỆU ======
async def auto_send_data(time_interval: int = 3600):
    while True:
        for device_id in connecting_devices:
            await send_data(device_id=device_id)
        await asyncio.sleep(time_interval)  # Thay đổi thời gian gửi dữ liệu nếu cần thiết


# ====== HÀM ĐỔI TÊN COLLECTION ======
async def rename_collection(old_name: str, new_name: str):
    if old_name in await db.list_collection_names():
        await db[old_name].rename(new_name)
        print(f"✅ Đã đổi tên collection từ '{old_name}' thành '{new_name}'")
    else:
        print(f"❌ Collection '{old_name}' không tồn tại.")

if __name__ == "__main__":
    # Ví dụ sử dụng hàm đổi tên collection
    asyncio.run(rename_collection("data_analyzed", "data_records"))