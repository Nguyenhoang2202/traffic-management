from pydantic import BaseModel, Field, root_validator
from enum import Enum
from typing import Optional
from datetime import datetime

# Enum cho vai trò người dùng
class UserRole(str, Enum):
    admin = "admin"
    supervisor = "supervisor"
    viewer = "viewer"

# Model người dùng
class User(BaseModel):
    id: Optional[str] = Field(None)  # nếu lưu MongoDB
    @root_validator(pre=True)
    def populate_id(cls, values):
        if "_id" in values:
            values["id"] = str(values["_id"])  # ánh xạ thủ công
        return values
    username: str
    email: str
    hashed_password: str
    role: UserRole = UserRole.viewer  # mặc định là viewer
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class createUser(BaseModel):
    username: str
    email: str
    password: str

class updateUser(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = UserRole.viewer   # có thể cập nhật vai trò

class loginUser(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str