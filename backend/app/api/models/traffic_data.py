from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TrafficData(BaseModel):
    device_id: str
    rain: Optional[float] = None
    mode: Optional[int] = None
    auto_mode: Optional[bool] = None
    timestamp: Optional[datetime] = None
    num_total: Optional[int] = None
    all_green_time: Optional[int] = None
    numb_turn_green: Optional[int] = None
    average_green_time: Optional[float] = None
