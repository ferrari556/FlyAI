from azure.storage.blob import BlobServiceClient, PublicAccess
from azure.core.exceptions import ResourceExistsError
from models.EffectSounds import EffectSounds
from models.EditHistory import EditHistory
from models.EffectSounds import EffectSounds
from models.Results import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydub import AudioSegment
import pytz, httpx, tempfile, contextlib, wave, os
from datetime import datetime

korea_time_zone = pytz.timezone("Asia/Seoul")
created_at_kst = datetime.now(korea_time_zone)

connect_str = "DefaultEndpointsProtocol=https;AccountName=ferrari556;AccountKey=g8BUEJyJPPinwIYo7QPyAZql3SHflcOXQHFfBSqWijNdor0uC3+2MFslBA16+AnoVvrT1G93xUQe+AStXt7N4g==;EndpointSuffix=core.windows.net"

# wav로 바꿔주는 함수
def convert_to_wav(file_path: str) -> str:
    audio = AudioSegment.from_file(file_path)
    tmp_path = tempfile.mktemp(".wav")  # 임시 파일 경로 생성
    audio.export(tmp_path, format="wav")
    return tmp_path

# wav 정보 길이 함수
def get_wav_length(wav_path: str) -> float:
    with contextlib.closing(wave.open(wav_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    return duration
    
async def upload_effect_sound_to_azure(file_name: str, file_path: str, db: AsyncSession):
    
    # 파일을 WAV 형식으로 변환
    converted_file_path = convert_to_wav(file_path)
    
    container_name = "effects"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # 컨테이너가 없으면 생성
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container(public_access=PublicAccess.Container)
    except ResourceExistsError:
        pass  # 컨테이너가 이미 존재하면 무시
        
    # 파일 업로드
    blob_client = container_client.get_blob_client(blob=file_name)
    with open(converted_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    blob_url = blob_client.url

    # 변환된 WAV 파일의 길이 정보 계산
    wav_length = get_wav_length(converted_file_path)

    # 파일 메타데이터와 wav 길이를 데이터베이스에 저장
    effect_sound = EffectSounds(
        result_id=1,  # result_id 설정이 필요하다면 적절한 값으로 변경
        Effect_Name=file_name,
        EffectFilePath=blob_url,
        EffectFileLength=wav_length,  # wav 파일 길이 정보 추가
        Upload_Date=created_at_kst
    )
    
    db.add(effect_sound)
    await db.commit()
    await db.refresh(effect_sound)

    # 임시 변환 파일 삭제
    os.remove(converted_file_path)
    
    return effect_sound

# 효과음 임시 파일 다운로드
async def download_file(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        # "./tmp" 디렉토리에 임시 파일 생성
        tmp = tempfile.NamedTemporaryFile(delete=False, dir="./tmp")
        tmp.write(resp.content)
        tmp.close()
        return tmp.name

# 오디오 분할 파일 + 효과음 파일 합쳐서 저장
async def combine_final_audio_files(db: AsyncSession, audio_id: int):

    result_files = await db.execute(
        select(Result).filter(Result.audio_id == audio_id).order_by(Result.Index)
    )
    result_files = result_files.scalars().all()

    combined_audio = AudioSegment.empty()

    for result_file in result_files:
        effect_history = await db.execute(
            select(EditHistory)
            .filter(EditHistory.result_id == result_file.result_id)
            .order_by(EditHistory.EditDate.desc())
            .limit(1)
        )
        effect_history = effect_history.scalars().first()

        # 파일 다운로드 및 오디오 세그먼트 생성
        audio_segment = AudioSegment.from_file(await download_file(result_file.ResultFilePath))

        # 최신 상태가 "Apply Effect"이고, 효과음 파일이 존재한다면 효과음 적용
        if effect_history and effect_history.Edit_Action == "Apply Effect":
            effect_sound = await db.get(EffectSounds, effect_history.effect_sound_id)
            effect_segment = AudioSegment.from_file(await download_file(effect_sound.EffectFilePath))
            audio_segment = audio_segment.overlay(effect_segment)

        combined_audio += audio_segment

    # 합쳐진 오디오 파일을 임시 파일로 저장하고 경로 반환
    final_audio_path = f"./tmp/final_audio_{audio_id}.wav"
    combined_audio.export(final_audio_path, format='wav')

    return final_audio_path

async def combine_audio_files_with_effects(db: AsyncSession, result_id: int, effect_sound_id: int):
    # 데이터베이스에서 오디오 파일 정보 가져오기
    audio_file = await db.get(Result, result_id)
    if not audio_file:
        return "오디오 파일을 찾을 수 없습니다."
    
    current_audio_segment = AudioSegment.from_file(audio_file.ResultFilePath)
    effect_sound = await db.get(EffectSounds, effect_sound_id)
    if not effect_sound:
        return "효과음을 찾을 수 없습니다."
    
    effect_segment = AudioSegment.from_file(effect_sound.EffectFilePath)
    combined_audio = current_audio_segment.overlay(effect_segment)
    
    # 합쳐진 오디오 파일 저장
    combined_audio_path = f'./tmp/combined_audio_{result_id}_{effect_sound_id}.wav'
    combined_audio.export(combined_audio_path, format='wav')
    
    return combined_audio_path