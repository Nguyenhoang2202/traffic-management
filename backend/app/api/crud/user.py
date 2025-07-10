from typing import List
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models import User,createUser,loginUser,updateUser,responseUser,updateRoleUser,updatePasswordUser
from ...auth.authentication import hash_password,verify_password, create_access_token
from bson import ObjectId

# AUTH
async def create_user(db: AsyncIOMotorDatabase, user: createUser):
    collection = db["users"]
    existing_user = await collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists") 
    
    hashed_password = hash_password(user.password)  
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
    ).model_dump(by_alias=True)
    await collection.insert_one(new_user)
    access_token = create_access_token(data={"username": new_user["username"]})
    return {"access_token": access_token, "token_type": "jwt"}

async def login_user(db: AsyncIOMotorDatabase, user_login: loginUser):
    collection = db["users"]
    user = await collection.find_one({"username": user_login.username, "is_active": True})
    if not user or not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = create_access_token(data={"username": user["username"]})
    return {"access_token": access_token, "token_type": "jwt"}

# GET
async def get_all_users(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100) -> List[responseUser]:
    collection = db["users"]
    cursor = collection.find({"is_active": True}).skip(skip).limit(limit)
    if cursor is None:
        raise HTTPException(status_code=404, detail="No users found")
    return [doc async for doc in cursor]

async def get_all_users_by_role(db: AsyncIOMotorDatabase, role: str, skip: int = 0, limit: int = 100) -> List[responseUser]:
    collection = db["users"]
    cursor = collection.find({"role":role,"is_active": True}).skip(skip).limit(limit)
    if cursor is None:
        raise HTTPException(status_code=404, detail="No users found")
    return [doc async for doc in cursor]

async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> responseUser:
    collection = db["users"]
    user = await collection.find_one({"_id": ObjectId(user_id), "is_active": True})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_user(db: AsyncIOMotorDatabase, username: str) -> responseUser:
    collection = db["users"]
    user = await collection.find_one({"username": username, "is_active": True})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# UPDATE
async def update_user(db: AsyncIOMotorDatabase, username: str, user_data: updateUser) -> responseUser:
    collection = db["users"]
    user = await collection.find_one({"username": username, "is_active": True})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user["_id"]
    update_dict = user_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No data to update")
    await collection.update_one({"username": username}, {"$set": update_dict})
    updated_user = await collection.find_one({"_id": user_id})
    return updated_user

async def update_user_role(db: AsyncIOMotorDatabase, username: str, user_data: updateRoleUser) -> responseUser:
    collection = db["users"]
    user = await collection.find_one({"username": username, "is_active": True})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_dict = user_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No data to update")
    await collection.update_one({"username": username}, {"$set": update_dict})
    updated_user = await collection.find_one({"username": username})
    return updated_user

async def update_user_password(db: AsyncIOMotorDatabase, username: str, user_data: updatePasswordUser) -> responseUser:
    collection = db["users"]
    user = await collection.find_one({"username": username, "is_active": True})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Kiểm tra mật khẩu cũ đúng không
    if not verify_password(user_data.old_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    # Hash mật khẩu mới
    hashed_password = hash_password(user_data.new_password)
    # Cập nhật mật khẩu mới vào DB
    await collection.update_one({"username": username}, {"$set": {"hashed_password": hashed_password}})
    return JSONResponse(
        status_code=200,
        content={"message": "Thay đổi mật khẩu thành công"}
    )

# DELETE
async def soft_delete_user(username: str, db: AsyncIOMotorDatabase):
    collection = db["users"]
    
    # Kiểm tra user tồn tại và đang hoạt động
    user = await collection.find_one({"username": username, "is_active": True})
    if not user:
        raise HTTPException(status_code=404, detail="Active user not found.")

    # Cập nhật trạng thái is_active thành False
    await collection.update_one(
        {"username": username},
        {"$set": {"is_active": False}}
    )

    return JSONResponse(
        status_code=200,
        content={"message": f"Người dùng '{username}' đã bị xóa (soft-deleted)."}
        )