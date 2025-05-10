from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List
from ..models import User, TokenResponse
from ..crud.user import *
from ...database.database import get_db
from ...auth.authorization import *
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter(prefix="/users", tags=["users"])

# Create user
@router.post("/", response_model=TokenResponse)
async def post_user(user: createUser, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        return await create_user(db=db, user=user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Test login user: user: OAuth2PasswordRequestForm = Depends()
# Work: user: loginUser
@router.post("/login", response_model=TokenResponse)
async def post_token_user(user: loginUser, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        return await login_user(db=db, user_login=user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Logout user
@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    # Xoá token bằng cách set lại cookie hết hạn
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="token_type", path="/")
    return {"message": "Logged out successfully"}

# Get all user
@router.get("/", response_model=List[User])
async def read_users(current_user: User = Depends(get_current_user),skip:int= 0,limit:int=100,db: AsyncIOMotorDatabase = Depends(get_db)):
    check_role(current_user.role, ["admin","supervisor"])
    try:
        return await get_all_users(db=db,skip=skip,limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get user by name
@router.get("/current_user", response_model=User)
async def read_user(current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        return await get_user(db=db, username=current_user.username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Get user by role
@router.get("/{role}", response_model=User)
async def read_users_by_role(role:str, current_user: User = Depends(get_current_user), skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_db)):
    check_role(current_user.role, ["admin"])
    try:
        return await get_all_users_by_role(db=db,role=role,skip=skip,limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Put user
@router.put("/{username}", response_model=User)
async def put_user(username: str, user_data: updateUser, current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    if (current_user.role != "admin") and (user_data.role != "viewer"):
        raise HTTPException(status_code=403, detail="You are not allowed to update role up!")
    try:
        return await update_user(db=db, username=username, user_data=user_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{username}")
async def unactive_user(username: str,current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    check_role(current_user.role, ["admin"])
    try:
        return await soft_delete_user(db=db, username=username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))