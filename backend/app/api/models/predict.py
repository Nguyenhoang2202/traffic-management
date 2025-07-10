from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PredictData(BaseModel):
    device_id: str
    prediction: Optional[float] = None
    predict_for_time: Optional[datetime] = None
    create_time: Optional[datetime] = None
    