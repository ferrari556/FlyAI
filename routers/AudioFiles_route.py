from models.AudioFiles import AudioFile, AudioDelete, AudioRead
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import audiofiles
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

# ID로 오디오 파일 읽기
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

# ID로 오디오 파일 삭제
@router.delete("/delete/{audio_id}", response_model=AudioDelete)
async def delete_audiofile(audio_id: int, db: AsyncSession = Depends(get_db)):
    try:
        existing_audiofile = await db.get(AudioFile, audio_id)
        if existing_audiofile is None:
            raise HTTPException(status_code=404, detail="Audio file not found")

        # 오디오 파일 정보를 기반으로 응답 데이터 생성
        response_data = {
            "file_name": existing_audiofile.file_name,
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