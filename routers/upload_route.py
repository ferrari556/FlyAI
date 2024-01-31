from fastapi import APIRouter, UploadFile, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from services.login_service import get_current_user_authorization
from services.upload_service import uploadtoazure, downloadfromazure
from models.users import User
from sqlalchemy.future import select
from services.login_service import oauth2_scheme

router = APIRouter()

@router.post("/upload", tags=["UploadFile"])
async def create_upload_file(request: Request, file: UploadFile, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    login_id = await get_current_user_authorization(request, token)
    user_id = await get_user_id_by_login_id(db, login_id)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    file_data = await file.read()
    return await uploadtoazure(file.filename, file.content_type, file_data, user_id, db)

async def get_user_id_by_login_id(db: AsyncSession, login_id: str):
    result = await db.execute(select(User).filter_by(login_id=login_id))
    user = result.scalar_one_or_none()
    return user.user_id if user else None

@router.post("/download")
async def download_and_save_file(request: Request, file_name: str, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    login_id = await get_current_user_authorization(request, token)
    user_id = await get_user_id_by_login_id(db, login_id)
    
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
       
    try:
        audio_file = await downloadfromazure(user_id, file_name, db)
        return {"message": "File downloaded and saved successfully", "audio_file": audio_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))