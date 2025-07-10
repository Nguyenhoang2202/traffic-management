import asyncio
import torch
from datetime import datetime, timedelta
import pandas as pd
from app.websocket_routers.device_connecting import connecting_devices
from app.predict.load_model import model, scaler
from app.database.database import get_db
from app.api.crud import get_data  # import hàm get_data từ CRUD

# Giả định Collection dùng để lưu kết quả dự đoán
PREDICT_COLLECTION_NAME = "predict_traffic"


def prepare_features(history: list) -> torch.Tensor:
    """
    Chuẩn hóa chuỗi 24 giờ gần nhất để đưa vào mô hình LSTM
    """
    features = []
    for entry in history:
        ts = pd.to_datetime(entry["timestamp"])
        hour = ts.hour
        weekday = ts.weekday()
        is_weekend = int(weekday >= 5)

        row = [
            entry["num_total"],
            entry["all_green_time"],
            entry["average_green_time"],
            int(entry["rain"]),
            hour,
            weekday,
            is_weekend
        ]
        features.append(row)

    features_scaled = scaler.transform(features)
    return torch.tensor(features_scaled, dtype=torch.float32).unsqueeze(0)  # shape: (1, 24, input_size)


async def predict_and_save(device_id):
    print(f"🔄 Bắt đầu task dự đoán cho thiết bị {device_id}")
    device = connecting_devices[device_id]
    db = await get_db()
    predict_collection = db[PREDICT_COLLECTION_NAME]

    while True:
        print("Có chạy predict")
        while not device.get("reset_predict"):
            await asyncio.sleep(1)

        create_time = datetime.utcnow()
        print(f"🚀 Thực hiện dự đoán cho thiết bị {device_id} lúc {create_time.isoformat()}")

        # Lấy dữ liệu từ CRUD thay vì truy vấn thủ công
        try:
            history = await get_data(db, device_id=device_id, skip=0, limit=24)
            if len(history) < 24:
                print(f"⚠️ Không đủ dữ liệu lịch sử cho thiết bị {device_id} (cần 24, có {len(history)})")
                device["reset_predict"] = False
                continue
        except Exception as e:
            print(f"❌ Lỗi khi gọi get_data: {e}")
            device["reset_predict"] = False
            continue

        # Chuẩn bị đầu vào
        try:
            input_tensor = prepare_features(history)
        except Exception as e:
            print(f"❌ Lỗi xử lý dữ liệu đầu vào: {e}")
            device["reset_predict"] = False
            continue

        with torch.no_grad():
            prediction = model(input_tensor).item()

        print(f"✅ Dự đoán lưu lượng: {prediction:.2f}")
        device["last_predict_data"] = prediction

        future_time = create_time + timedelta(hours=1)
        
        try:
            result = await predict_collection.insert_one({
                "device_id": device_id,
                "prediction": prediction,
                "predict_for_time": future_time,
                "create_time": create_time,
            })
            print(f"✅ Đã lưu dự đoán vào DB với _id: {result.inserted_id}")
        except Exception as e:
            print(f"❌ Lỗi khi lưu DB: {e}")

        device["reset_predict"] = False
        await asyncio.sleep(1)


# Quản lý các task dự đoán
predicting_tasks = {}

async def run_all_predict_tasks_forever():
    while True:
        for device_id in connecting_devices:
            if device_id not in predicting_tasks:
                task = asyncio.create_task(predict_and_save(device_id))
                predicting_tasks[device_id] = task
                print(f"✅ Đã tạo task DỰ ĐOÁN cho: {device_id}")

        disconnected_ids = [did for did in predicting_tasks if did not in connecting_devices]
        for did in disconnected_ids:
            task = predicting_tasks.pop(did)
            if not task.done():
                task.cancel()
                print(f"⚠️ Đã hủy task dự đoán cho thiết bị {did} do mất kết nối")

        await asyncio.sleep(2)
