from pydantic import BaseModel

    
# users 테이블
class users(BaseModel): 
    user_id : int          
    login_id : str          
    login_pw : str                


# AudioFiles 테이블
class AudioFiles(BaseModel): 
    audio_id : int
    user_id : int
    audio_name : str
    filepath : str
    filetype : str
    file_status : str


# STT Data 테이블
class STTdata(BaseModel): 
    text_id : int
    audio_id : int
    text : str


# Effectsounds 테이블
class Effectsounds(BaseModel): 
    effect_id : int
    effect_name : str
    effect_path : str
    Effect_number : int



# UserEdits 테이블
class UserEdits(BaseModel): 
    user_edit_id : int
    user_id : int
    audio_id : int
    effect_id : int
    effect_status : str



# EditSession 테이블
class EditSession(BaseModel): 
    session_id : int
    user_id : int
    audio_id : int
    effect_id: int
    session_status : str



# EditHistory 테이블
class EditHistory(BaseModel): 
    history_id: int
    session_id : int
    user_id : int



# UserSoundEffects 테이블 (다대다 관계를 해소하기 위한 중간 테이블)
class UserSoundEffects(BaseModel): 
    user_id : int
    effect_id : int
