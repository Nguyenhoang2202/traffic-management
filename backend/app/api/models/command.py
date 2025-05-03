from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class Command(BaseModel):
    user_id: Optional[str] = None 
    device_id: str                
    mode: Optional[int] = None
    auto_mode: Optional[bool] = None
    green_time: Optional[int] = None
    red_time: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)