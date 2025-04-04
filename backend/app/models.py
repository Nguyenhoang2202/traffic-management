from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict

class Camera(BaseModel):
    camera_id: str
    lat: float
    long: float
    registered_at: datetime = datetime.utcnow()

class CameraData(BaseModel):
    camera_id: str
    timestamp: datetime = datetime.utcnow()
    frame: Optional[str] = None  # Base64
    sensor_data: Dict[str, str]
