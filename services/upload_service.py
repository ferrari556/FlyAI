from fastapi import HTTPException
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from models.AudioFiles import AudioFile
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
import pytz, datetime, os, mimetypes, librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
from sqlalchemy.future import select
from mutagen.mp3 import MP3

connect_str = "DefaultEndpointsProtocol=https;AccountName=ferrari556;AccountKey=g8BUEJyJPPinwIYo7QPyAZql3SHflcOXQHFfBSqWijNdor0uC3+2MFslBA16+AnoVvrT1G93xUQe+AStXt7N4g==;EndpointSuffix=core.windows.net"

# 오디오 파일 전처리
class AudioProcessor:
    def __init__(self, id, wav_path, output_dir):
        self.id = id
        self.wav_path = wav_path
        self.output_dir = output_dir

    def convert_audio_type(self):
        audSeg = AudioSegment.from_mp3(self.wav_path)
        audSeg.export(self.wav_path, format="wav")


    def _split_array(self, arr, c, n):
        result_arr = []
        result_idx = [0,]
        current_group = [arr[0]]
        count = 1
        idx_counter = 1 # 인덱스 슬라이싱은 마지막 인덱스 미포함이니까

        for i in range(1, len(arr)):
            idx_counter += 1
            current_group.append(arr[i])
            if arr[i] <= c:
                if arr[i-1]<=c:
                    count += 1
                else:
                    count = 1
            if count>=n and len(arr)>idx_counter+1 and arr[i+1]>c:
                result_idx.append(idx_counter)
                result_arr.append(current_group.copy())
                current_group.clear()
                count = 1

        if len(current_group)!=0:
            result_arr.append(current_group.copy())

        result_idx.append(len(arr))

        return result_arr, result_idx


    def _split_and_save(self, criteria, num):
        """
        - wav_path : 로드할 WAV 파일의 경로
        - output_dir : WAV 파일들을 저장할 디렉토리 경로
        - segment_length : 분할할 세그먼트의 길이 (초 단위, 기본값은 30초)
        """
        
        # 출력 디렉토리가 존재하지 않으면 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # wav 파일 로드합니다.
        y, sr = librosa.load(self.wav_path, sr=None)

        gap = []
        for i in range(1, len(y)):
            a = abs(y[i-1]-y[i])
            gap.append(a)
        
        gap = np.array(gap)

        arr, idx = self._split_array(gap, criteria, num)

        # 지정된 길이 segment_samples로 분할하여 WAV 파일로 저장
        for i in range(len(idx)-1):
            start_sample = idx[i]
            end_sample = idx[i+1]
            output_path = f"{self.output_dir}/{self.id}_{i}-1.wav"

            # 여기서는 segment로 분할된 오디오 데이터를 WAV 파일로 저장한다.
            sf.write(output_path, y[start_sample:end_sample], sr)


    def _critria_mean(self, y):
        filtered_values = y[y <= 0.01]
        average_value = np.mean(filtered_values)
        return average_value

    def _critria_med(self, y):
        filtered_values = y[y <= 0.01]
        max_value = np.median(filtered_values)
        return max_value

    def _all_duration(self, arr, c):
        res_dur = []
        current_group = []
        count = 1
        s = 0

        for i in range(len(arr)):
            if arr[i] <= c:
                if s==0:
                    s=1
                current_group.append(arr[i])
            if s==1 and arr[i]>c:
                res_dur.append(len(current_group))
                current_group.clear()
                s=0

        if len(current_group)!=0:
            res_dur.append(len(current_group))

        res_dur = np.array(res_dur)
        filtered_values = res_dur[res_dur > 10000]
        return filtered_values


    def process_audio(self):

        # Convert MP3 to WAV
        # self.convert_audio_type()

        # Load the WAV file
        y, sr = librosa.load(self.wav_path, sr=None)

        
        # Calculate the absolute differences
        tmp = [abs(y[i-1] - y[i]) for i in range(1, len(y))]
        y_a = np.array(tmp)

        # Calculate criteria values
        medc = self._critria_med(y_a)
        meanc = self._critria_mean(y_a)
        dur_mean = self._all_duration(y_a, medc)  #0.05
        mind_meanc = np.max(dur_mean)

        # Split and save the audio
        self._split_and_save(meanc, mind_meanc)
        
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
        
        # 추가된 분할 로직
        output_dir = f"./processed_audio/user_id_{user_id}"  # 분할된 파일을 저장할 디렉토리
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 분할 로직을 위한 다운로드 로직 필요 (blob_url 사용)
        # 여기서는 로컬 파일 경로(temp_file_path)를 사용
        processor = AudioProcessor(user_id, temp_file_path, output_dir)
        processor.process_audio()
       
    except Exception as e:       
        # 예외 처리 블록에서 blob_client가 None인지 확인합니다.
        if blob_client is not None:
            await blob_client.delete_blob()
        raise e
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        pass

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
    
async def get_user_id_by_login_id(db: AsyncSession, login_id: str):
    result = await db.execute(select(User).filter_by(login_id=login_id))
    user = result.scalar_one_or_none()
    return user.user_id if user else None