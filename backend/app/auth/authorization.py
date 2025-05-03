from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError
from .authentication import decode_access_token
from ..database.database import get_db
from ..api.models import User
from motor.motor_asyncio import AsyncIOMotorDatabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    user = await db["users"].find_one({"username": payload["username"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return User(**user)


def check_role(role:str, allowed_roles: list[str]):
    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="You are not allowed.")
