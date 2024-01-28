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
    audio_name : str
    FilePath : str
    File_Length : float
    FileType : str
    Complete_Date : datetime
    File_Status : str
    
# STT Data 테이블
class sttdata(BaseModel): 
    text_id : int
    audio_id : int
    Converted_text : str
    Complete_Convert_Date : datetime

# Effectsounds 테이블
class effectsounds(BaseModel): 
    effect_id : int
    effect_name : str
    Effect_Path : str
    Effect_Length : float
    Effect_number : int

# UserEdits 테이블
class useredits(BaseModel): 
    user_edit_id : int
    user_id : int
    audio_id : int
    effect_id : int
    text_position : int
    effect_status : str
    
# EditSession 테이블
class editsession(BaseModel): 
    session_id : int
    user_id : int
    audio_id : int
    effect_id: int
    Edit_start : datetime
    Edit_finish : datetime
    Editposition : int
    session_status : str

# EditHistory 테이블
class edithistory(BaseModel): 
    history_id: int
    session_id : int
    user_id : int
    ChangeContent : str
    ChangeTime : datetime

# UserSoundEffects 테이블 (다대다 관계를 해소하기 위한 중간 테이블)
class usersoundeffects(BaseModel): 
    id : int
    user_id : int
    effect_id : int
