import torch
import pickle
import os
from app.predict.traffic_lstm_model import TrafficLSTM  # Lớp mô hình bạn định nghĩa

# Đường dẫn tuyệt đối tới thư mục gốc dự án
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Đường dẫn tới model và scaler
MODEL_PATH = os.path.join(BASE_DIR, "predict", "predict_traffic_lstm.pth")
SCALER_PATH = os.path.join(BASE_DIR, "predict", "traffic_scaler.pkl")

# Biến toàn cục để giữ mô hình và scaler đã load
model = None
scaler = None

def load_model_and_scaler():
    global model, scaler

    # Load mô hình
    model = TrafficLSTM(input_size=7)  # Nếu bạn có thêm params khác thì truyền vào
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()

    # Load scaler
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)

    print("✅ Mô hình và scaler đã được load thành công.")
