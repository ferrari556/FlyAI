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
    File_Name : str
    FilePath : str
    File_Length : float
    FileType : str
    Upload_Date : datetime
    File_Status : str

class Result(BaseModel):
    result_id : int
    audio_id : int
    Index : int
    Converted_Result : str
    Is_Text : bool
    EffectFilePath : str
    Converted_Date : datetime
    
# UserEdits 테이블
class useredits(BaseModel): 
    user_edit_id : int
    user_id : int
    audio_id : int
    result_id : int
    Applied_Effect : bool

# EditSession 테이블
class editsession(BaseModel): 
    session_id : int
    user_id : int
    audio_id : int
    result_id: int
    Start_Edit : datetime
    End_Edit : datetime
    LastEditPoint : int
    Session_State : str
    
# EditHistory 테이블
class edithistory(BaseModel): 
    history_id: int
    session_id : int
    result_id : int
    Edit_Action : str
    Original_Text : str
    Edited_Text : str
    EditDate : datetime
