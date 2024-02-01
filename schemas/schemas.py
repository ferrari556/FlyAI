from sqlalchemy import Column, String, Integer, DateTime, func
from datetime import datetime
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel, validator
    
# users 테이블
class users(BaseModel): 
    user_id : int          
    login_id : str          
    login_pw : str                
    created_at : datetime

# AudioFiles 테이블
class audiofiles(BaseModel): 
    audio_id : int
    user_id : int
    file_name : str
    FilePath : str
    File_Length : float
    FileType : str
    Upload_Date : datetime
    File_Status : str
    
# STT Data 테이블
class sttdata(BaseModel): 
    text_id : int
    audio_id : int
    Converted_text : str
    Converted_Date : datetime

# Effectsounds 테이블
class effectsounds(BaseModel): 
    effect_id : int
    effect_name : str
    effect_path : str
    effect_length : float
    effect_index : int

# UserEdits 테이블
class useredits(BaseModel): 
    user_edit_id : int
    user_id : int
    audio_id : int
    effect_id : int
    text_position : int
    effect_status : str
    session_status : str

# EditSession 테이블
class editsession(BaseModel): 
    session_id : int
    user_id : int
    audio_id : int
    effect_id: int
    start_edit : datetime
    end_edit : datetime
    LastEditPoint : int
    
# EditHistory 테이블
class edithistory(BaseModel): 
    history_id: int
    session_id : int
    user_id : int
    EditContent : str
    EditDate : datetime

# UserSoundEffects 테이블 (다대다 관계를 해소하기 위한 중간 테이블)
class usersoundeffects(BaseModel): 
    id : int
    user_id : int
    effect_id : int
