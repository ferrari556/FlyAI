from fastapi import HTTPException
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from models.AudioFiles import AudioFile
from sqlalchemy.ext.asyncio import AsyncSession
import pytz, datetime
from sqlalchemy.future import select
from mutagen.mp3 import MP3
import os
import mimetypes

connect_str = "DefaultEndpointsProtocol=https;AccountName=ferrari556;AccountKey=g8BUEJyJPPinwIYo7QPyAZql3SHflcOXQHFfBSqWijNdor0uC3+2MFslBA16+AnoVvrT1G93xUQe+AStXt7N4g==;EndpointSuffix=core.windows.net"

# 파일 이름으로 오디오 파일 검색
async def get_audiofile_by_name(db: AsyncSession, File_Name: str):
    result = await db.execute(select(AudioFile).filter_by(File_Name=File_Name))
    return result.scalar_one_or_none()

async def uploadtoazure(File_Name: str, content_type: str, file_data, user_id: int, db: AsyncSession):
    # 파일 이름으로 기존 오디오 파일 존재 여부 확인
    existing_audiofile = await get_audiofile_by_name(db, File_Name)
    if existing_audiofile:
        raise ValueError("File Name Already Used")

    # 로컬 경로에 파일 임시 저장
    temp_file_path = f"./tmp/{File_Name}"
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_data)

    # Azure 연결 문자열 설정
    container_name = f"test{user_id}"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = None
    
    try:
        # MP3 파일의 재생 시간 계산
        audio = MP3(temp_file_path)
        file_length = audio.info.length  # 재생 시간 (초 단위)
        
        # 컨테이너 생성 (존재하지 않는 경우에만)
        try:
            blob_service_client.create_container(container_name)
        except ResourceExistsError:
            pass
        
        # blob client 생성
        blob_client = blob_service_client.get_container_client(container_name).get_blob_client(File_Name)
        
        # blob에 file upload
        blob_client.upload_blob(file_data)

        # Blob의 URL을 얻습니다.
        blob_url = blob_client.url
        
        # 데이터베이스 업데이트
        korea_time_zone = pytz.timezone("Asia/Seoul")
        created_at_kst = datetime.datetime.now(korea_time_zone)

        audio_file = AudioFile(
            user_id=user_id,
            File_Name=File_Name,
            FilePath=blob_url,
            File_Length=file_length,
            FileType=content_type,
            Upload_Date=created_at_kst,
            File_Status="Uploaded"
        )

        db.add(audio_file)
        await db.commit()
    except Exception as e:
        # 파일 업로드 중 에러 발생 시 Blob에서 파일 삭제
        await blob_client.delete_blob()
        raise e
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return audio_file

# Azure에서 파일 다운로드 및 AudioFiles 데이터베이스에 저장
async def downloadfromazure(user_id: int, File_Name: str, db: AsyncSession):
    container_name = f"test{user_id}"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=File_Name)
    temp_file_path = f"./tmp/{File_Name}"
    
    try:
        # Blob에서 파일 다운로드 시도
        with open(temp_file_path, "wb") as file:
            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())
            
    except ResourceNotFoundError:
        # Blob Storage에 파일이 없는 경우 예외 처리
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=404, detail="Blob not found")

    # 파일이 성공적으로 다운로드 된 경우, 파일 정보 추출 및 저장
    try:
        audio = MP3(temp_file_path)
        file_length = audio.info.length
        content_type, _ = mimetypes.guess_type(File_Name)

        korea_time_zone = pytz.timezone("Asia/Seoul")
        created_at_kst = datetime.datetime.now(korea_time_zone)

        audio_file = AudioFile(
            user_id=user_id,
            File_Name=File_Name,
            FilePath=blob_client.url,
            File_Length=file_length,
            FileType=content_type,
            Upload_Date=created_at_kst,
            File_Status="Downloaded"
        )

        db.add(audio_file)
        await db.commit()
        await db.refresh(audio_file)
        return audio_file
    except Exception as e:
        # 다른 예외 발생 시 처리
        raise HTTPException(status_code=500, detail=str(e))