from fastapi import HTTPException
from azure.storage.blob import BlobServiceClient, PublicAccess
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from models.AudioFiles import AudioFile
from models.users import User
from models.Results import Result
from models.EditHistory import EditHistory
from pydub import AudioSegment
from models.EffectSounds import EffectSounds
from sqlalchemy.ext.asyncio import AsyncSession
from services.audio_processing import AudioProcessor
import pytz, datetime, os, mimetypes, wave, contextlib
from sqlalchemy.future import select
from mutagen.mp3 import MP3
from typing import List


connect_str = "DefaultEndpointsProtocol=https;AccountName=ferrari556;AccountKey=g8BUEJyJPPinwIYo7QPyAZql3SHflcOXQHFfBSqWijNdor0uC3+2MFslBA16+AnoVvrT1G93xUQe+AStXt7N4g==;EndpointSuffix=core.windows.net"

# wav 파일 길이 정보 함수
def get_wav_length(wav_path):
    with contextlib.closing(wave.open(wav_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration
    
# 파일 이름과 사용자 ID로 오디오 파일 검색
async def get_audiofile_by_name(db: AsyncSession, user_id: int, File_Name: str):
    result = await db.execute(select(AudioFile).filter(AudioFile.user_id == user_id, AudioFile.File_Name == File_Name))
    return result.scalars().first()

# 분할 파일 데이터베이스에 저장
async def split_and_save_results(db : AsyncSession, audio_id: int, segments_info: List[str], segment_lengths: List[float]):
    if segments_info is None:
        raise ValueError("segments_info is None, which indicates no segments were processed or returned.")
    
    results = []
    
    for index, (segment_path, segment_length) in enumerate(zip(segments_info, segment_lengths)):
        # 여기에서 segment_length 값을 Result 객체에 저장
        result = Result(
            audio_id=audio_id,
            Index=index + 1,
            Converted_Result="X",
            ResultFilePath=segment_path,
            ResultFileLength=segment_length,  # 세그먼트 길이 저장
            Converted_Date=datetime.datetime.now()
        )
        db.add(result)
        results.append(result)  # 결과 리스트에 추가
    await db.commit()
    
    # 결과 객체의 리스트를 반환
    return results
    
# Azure Blob Storage로 분할 파일과 원본 파일 업로드
async def uploadtoazure(File_Name: str, content_type: str, file_data, user_id: int, db: AsyncSession):
    
    # 파일 이름으로 기존 오디오 파일 존재 여부 확인
    existing_audiofile = await get_audiofile_by_name(db, user_id, File_Name)
    if existing_audiofile:
        raise ValueError("File Name Already Used")

    output_dir = f"./tmp"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 로컬 경로에 파일 임시 저장
    temp_file_path = f"./tmp/{File_Name}"
    
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_data)

    # Azure 연결 문자열 설정
    container_name = f"metadata{user_id}"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = None
    
    try:
        file_length = get_wav_length(temp_file_path)
        
        # 컨테이너 생성 및 공개 접근 수준 설정 (Container 또는 Blob)
        try:
            blob_service_client.create_container(container_name, public_access=PublicAccess.Container)
        except ResourceExistsError:
            pass
        
        blob_client = blob_service_client.get_container_client(container_name).get_blob_client(File_Name)    

        blob_client.upload_blob(file_data, overwrite=True)
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
        await db.refresh(audio_file)
        
        # 오디오 파일 처리
        output_dir = f"./processed_audio/user{user_id}"
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        container_name = f"processed-audio{user_id}"
        
        # 컨테이너 생성 및 공개 접근 수준 설정 (Container 또는 Blob)
        try:
            blob_service_client.create_container(container_name, public_access=PublicAccess.Container)
        except ResourceExistsError:
            pass
        
        processor = AudioProcessor(audio_file.audio_id, temp_file_path, output_dir, blob_service_client, container_name)
        segments_info, segment_lengths = processor.process_audio()
        results = await split_and_save_results(db, audio_file.audio_id, segments_info, segment_lengths)
              
    except Exception as e:
        # blob_client가 초기화되었고, 예외 발생 시 해당 blob 삭제
        if blob_client:
            try:
                await blob_client.delete_blob()  # blob 삭제 시도
            except Exception as delete_error:
                print(f"Failed to delete blob: {delete_error}")
        raise e  # 원래 발생한 예외 다시 발생시킴

    finally:
        # 함수 종료 전에 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return results

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
    
async def get_user_id_by_login_id(db: AsyncSession, login_id: str):
    result = await db.execute(select(User).filter_by(login_id=login_id))
    user = result.scalar_one_or_none()
    return user.user_id if user else None

async def get_audio_id_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(AudioFile).where(AudioFile.user_id == user_id).order_by(AudioFile.audio_id.desc()).limit(1)
    )
    audio = result.scalar_one_or_none()  # 여기서는 first()를 사용해 첫 번째 결과만 가져옵니다.
    return audio.audio_id if audio else None

async def get_audiofile_by_id(db: AsyncSession, audio_id: int):
    audiofile = await db.get(AudioFile, audio_id)
    if audiofile is None:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return audiofile

async def delete_audiofile(db: AsyncSession, audio_id: int):
    existing_audiofile = await db.get(AudioFile, audio_id)
    if existing_audiofile is None:
        raise HTTPException(status_code=404, detail="Audio file not found")
    await db.delete(existing_audiofile)
    await db.commit()
    return {
        "File_Name": existing_audiofile.File_Name,
        "FileType": existing_audiofile.FileType,
        "Upload_Date": existing_audiofile.Upload_Date
    }
    
async def combine_audio_files(db: AsyncSession, audio_id: int):
    async with db.begin():
        # 해당 오디오 ID에 속한 모든 결과 파일을 순서대로 가져옵니다.
        result_files = await db.execute(
            select(Result).filter(Result.audio_id == audio_id).order_by(Result.Index)
        )
        result_files = result_files.scalars().all()

        # 최종 오디오 파일 초기화
        combined_audio = AudioSegment.empty()

        for result_file in result_files:
            audio_segment = AudioSegment.from_file(result_file.ResultFilePath)

            # 해당 result_id에 대한 최신 'Apply Effect' 액션을 가져옵니다.
            effect_history = await db.execute(
                select(EditHistory).filter(
                    EditHistory.result_id == result_file.result_id,
                    EditHistory.Edit_Action == "Apply Effect"
                ).order_by(EditHistory.EditDate.desc())
            )
            effect_history = effect_history.scalars().first()

            if effect_history:
                effect_sound = await db.get(EffectSounds, effect_history.effect_sound_id)
                effect_segment = AudioSegment.from_file(effect_sound.EffectFilePath)
                audio_segment = audio_segment.overlay(effect_segment)

            combined_audio += audio_segment

        # 합쳐진 오디오 파일을 저장합니다.
        combined_audio_path = f"final_audio_{audio_id}.mp3"
        combined_audio.export(combined_audio_path, format="mp3")

        return combined_audio_path