from sqlalchemy.orm import Session
from models.AudioFiles import AudioFile
from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import AudioFiles
from fastapi.responses import JSONResponse
from config.database import get_db

router = APIRouter()

@router.get("/audiofiles", tags=["AudioFiles"])
async def get_all_audiofiles(db: Session = Depends(get_db)):
    try:
        audiofiles = db.query(AudioFile).all()
        return audiofiles
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

# ID로 오디오 파일 읽기
@router.get("/audiofiles/{audio_id}", tags=["AudioFiles"])
async def get_audiofile_by_id(audio_id: int, db: Session = Depends(get_db)):
    try:
        audiofile = db.query(AudioFile).filter(AudioFile.audio_id == audio_id).first()
        if audiofile is None:
            raise HTTPException(status_code=404, detail="Audio file not found")
        return audiofile
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

# 새로운 오디오 파일 생성
@router.post("/audiofiles", tags=["AudioFiles"])
async def create_audiofile(audiofile: AudioFiles, db: Session = Depends(get_db)):
    try:
        new_audiofile = AudioFile(
            user_id=audiofile.user_id, 
            audio_name=audiofile.audio_name,
            FilePath=audiofile.FilePath,
            File_Length=audiofile.File_Length,
            FileType=audiofile.FileType,
            Complete_Date=audiofile.Complete_Date,
            File_Status=audiofile.File_Status
        )
        db.add(new_audiofile)
        db.commit()
        db.refresh(new_audiofile)
        return new_audiofile
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

# 오디오 파일 업데이트
@router.put("/audiofiles/{audio_id}", tags=["AudioFiles"])
async def update_audiofile(audio_id: int, audiofile: AudioFiles, db: Session = Depends(get_db)):
    try:
        existing_audiofile = db.query(AudioFile).filter(AudioFile.audio_id == audio_id).first()
        if existing_audiofile is None:
            raise HTTPException(status_code=404, detail="Audio file not found")

        existing_audiofile.user_id = audiofile.user_id
        existing_audiofile.audio_name = audiofile.audio_name
        existing_audiofile.FilePath = audiofile.FilePath
        existing_audiofile.File_Length = audiofile.File_Length
        existing_audiofile.FileType = audiofile.FileType
        existing_audiofile.Complete_Date = audiofile.Complete_Date
        existing_audiofile.File_Status = audiofile.File_Status

        db.commit()
        db.refresh(existing_audiofile)
        return existing_audiofile
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()

# ID로 오디오 파일 삭제
@router.delete("/audiofiles/{audio_id}", tags=["AudioFiles"])
async def delete_audiofile(audio_id: int, db: Session = Depends(get_db)):
    try:
        existing_audiofile = db.query(AudioFile).filter(AudioFile.audio_id == audio_id).first()
        if existing_audiofile is None:
            raise HTTPException(status_code=404, detail="Audio file not found")

        db.delete(existing_audiofile)
        db.commit()
        return {"message": "Audio file deleted"}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})
    finally:
        db.close()