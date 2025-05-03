from pydantic import BaseModel
from typing import Optional

class Camera(BaseModel):
    device_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


