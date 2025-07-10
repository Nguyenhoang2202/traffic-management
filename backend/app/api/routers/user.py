from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List
from ..models import User, TokenResponse,responseUser
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
@router.get("/", response_model=List[responseUser])
async def read_users(current_user: User = Depends(get_current_user),skip:int= 0,limit:int=100,db: AsyncIOMotorDatabase = Depends(get_db)):
    check_role(current_user.role, ["admin","supervisor"])
    try:
        return await get_all_users(db=db,skip=skip,limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get current user
@router.get("/current_user/", response_model=responseUser)
async def read_user(current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        return await get_user(db=db, username=current_user.username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/user_id/{user_id}", response_model=responseUser)
async def read_user(user_id:str,current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    check_role(current_user.role, ["admin","supervisor"])
    try:
        return await get_user_by_id(db=db, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Get user by role
@router.get("/{role}", response_model=List[responseUser])
async def read_users_by_role(role:str, current_user: User = Depends(get_current_user), skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_db)):
    check_role(current_user.role, ["admin","supervisor"])
    try:
        return await get_all_users_by_role(db=db,role=role,skip=skip,limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Put user
@router.put("/me/", response_model=responseUser)
async def update_current_user(
    user_data: updateUser,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    # Chỉ user đang đăng nhập được tự sửa thông tin
    return await update_user(db, current_user.username, user_data)


@router.put("/me/password/", response_model=responseUser)
async def update_current_user_password(
    user_data: updatePasswordUser,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await update_user_password(db, current_user.username, user_data)


@router.put("/role/{username}", response_model=responseUser)
async def update_role(
    username: str,
    user_data: updateRoleUser,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    check_role(current_user.role, ["admin"])  # Bắt buộc phải là admin mới được đổi role
    return await update_user_role(db, username, user_data)

# Delete
@router.delete("/{username}")
async def unactive_user(username: str,current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    check_role(current_user.role, ["admin"])
    try:
        return await soft_delete_user(db=db, username=username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))