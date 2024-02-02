from models.AudioFiles import AudioFile, AudioDelete, AudioRead
from models.AudioFiles import AudioResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Request
from fastapi.responses import JSONResponse
from config.database import get_db
from services.login_service import get_current_user_authorization
from services.upload_service import uploadtoazure, downloadfromazure, get_user_id_by_login_id
from services.login_service import oauth2_scheme

router = APIRouter()

# audio_id로 오디오 파일 읽기
@router.get("/read/{audio_id}", response_model = AudioRead)
async def get_audiofile_by_id(audio_id: int, db: AsyncSession = Depends(get_db)):
    try:
        audiofile = await db.get(AudioFile, audio_id)
        if audiofile is None:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return audiofile
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

# audio_id로 오디오 파일 삭제
@router.delete("/delete/{audio_id}", response_model=AudioDelete)
async def delete_audiofile(audio_id: int, db: AsyncSession = Depends(get_db)):
    try:
        existing_audiofile = await db.get(AudioFile, audio_id)
        if existing_audiofile is None:
            raise HTTPException(status_code=404, detail="Audio file not found")

        # 오디오 파일 정보를 기반으로 응답 데이터 생성
        response_data = {
            "File_Name": existing_audiofile.File_Name,
            "FileType": existing_audiofile.FileType,
            "Upload_Date": existing_audiofile.Upload_Date
        }

        await db.delete(existing_audiofile)
        await db.commit()
        return response_data
    except Exception as e:
        await db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        await db.close()
  
# Azure Blob Storage로 파일 업로드      
@router.post("/upload")
async def create_upload_file(request: Request, file: UploadFile, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    login_id = await get_current_user_authorization(request, token)
    user_id = await get_user_id_by_login_id(db, login_id)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    file_data = await file.read()
    return await uploadtoazure(file.filename, file.content_type, file_data, user_id, db)

# Azure Blob Storage에서 파일 다운로드   
@router.post("/download", response_model = AudioResponse)
async def download_and_save_file(request: Request, File_Name: str, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    login_id = await get_current_user_authorization(request, token)
    user_id = await get_user_id_by_login_id(db, login_id)
    
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
       
    try:
        db_audio_file = await downloadfromazure(user_id, File_Name, db)
        return db_audio_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))