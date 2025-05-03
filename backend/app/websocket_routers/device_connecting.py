import base64
import numpy as np
import cv2

connecting_devices = {}

def get_frame_from_device(device_id: str) -> np.ndarray:
    """
    Trích xuất và giải mã frame từ thiết bị dựa trên ID.
    """
    try:
        base64_str = connecting_devices[device_id]["last_data"]["image"]
        if not base64_str:
            raise ValueError("No image data found")

        image_data = base64.b64decode(base64_str)
        np_arr = np.frombuffer(image_data, dtype=np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Không thể decode ảnh (ảnh rỗng hoặc lỗi)")
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    except KeyError:
        raise KeyError(f"Device ID '{device_id}' không tồn tại hoặc không có dữ liệu")
    except Exception as e:
        raise ValueError(f"Không thể giải mã ảnh từ thiết bị {device_id}: {e}")