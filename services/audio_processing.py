from azure.storage.blob import BlobServiceClient
from pydub import AudioSegment
import os, librosa, soundfile as sf, numpy as np

# 오디오 파일 전처리
class AudioProcessor:
    def __init__(self, id, wav_path, output_dir, blob_service_client: BlobServiceClient, container_name: str):
        self.id = id
        self.wav_path = wav_path
        self.output_dir = output_dir
        self.blob_service_client = blob_service_client
        self.container_name = container_name

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
        y, sr = librosa.load(self.wav_path, sr=16000)

        gap = []
        for i in range(1, len(y)):
            a = abs(y[i-1]-y[i])
            gap.append(a)
        
        gap = np.array(gap)

        arr, idx = self._split_array(gap, criteria, num)
        segment_paths = []
        
        for i in range(len(idx)-1):
            start_sample = idx[i]
            end_sample = idx[i+1]
            segment_path = f"{self.output_dir}/{self.id}_{i}.wav"  # Define the path for this segment
            sf.write(segment_path, y[start_sample:end_sample], sr)  # Save the segment
            segment_paths.append(segment_path)  # Add the path to the list

        return segment_paths  # Return the list of paths

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

    def upload_file_to_azure(self, file_path: str):
        """
        Azure Blob Storage에 파일을 업로드합니다.
        """
        blob_name = os.path.basename(file_path)
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        
    def process_audio(self):

        # Load the WAV file
        y, sr = librosa.load(self.wav_path, sr=16000)

        
        # Calculate the absolute differences
        tmp = [abs(y[i-1] - y[i]) for i in range(1, len(y))]
        y_a = np.array(tmp)

        # Calculate criteria values
        medc = self._critria_med(y_a)
        meanc = self._critria_mean(y_a)
        dur_mean = self._all_duration(y_a, medc)  #0.05
        # mind_meanc = np.max(dur_mean)

        segment_paths = self._split_and_save(meanc, 16000)
        # 분할된 파일들을 Azure Blob Storage에 업로드합니다.
        for segment_path in segment_paths:
            self.upload_file_to_azure(segment_path)

        return segment_paths