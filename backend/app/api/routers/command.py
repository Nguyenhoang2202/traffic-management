from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models import Command, User
from ..crud.command import *
from ...database.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from ...auth.authorization import *
router = APIRouter(prefix="/commands", tags=["commands"])

@router.post("/", response_model=Command)
async def create_commands(command: Command,current_user: User = Depends(get_current_user),db: AsyncIOMotorDatabase = Depends(get_db)):
    check_role(current_user.role, ["admin","supervisor"])
    try:
        user_id = current_user.id
        command.user_id = user_id
        return await create_command(db=db, command=command)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/", response_model=List[Command])
async def read_commands(current_user: User = Depends(get_current_user),db: AsyncIOMotorDatabase = Depends(get_db)):
    check_role(current_user.role, ["admin","supervisor"])
    try:
        return await get_all_commands(db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{user_id}", response_model=List[Command])
async def read_user_commands(user_id: str, current_user: User = Depends(get_current_user),db: AsyncIOMotorDatabase = Depends(get_db)):
    check_role(current_user.role, ["admin","supervisor"])
    try:
        return await get_user_commands(db=db, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))