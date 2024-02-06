from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from datetime import datetime

class EditHistory(Base):
    __tablename__ = 'EditHistory'
    history_id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('EditSession.session_id'))
    result_id = Column(Integer, ForeignKey('Result.result_id'))
    audio_id = Column(Integer, ForeignKey('AudioFile.audio_id'))
    Edit_Action = Column(String(30))
    Original_Text = Column(String(255))
    Edited_Text = Column(String(255))
    EditDate = Column(DateTime)
    
    # 1:N 관계 설정
    result = relationship("Result")
    audio_file = relationship("AudioFile")
    edit_session = relationship('EditSession', foreign_keys=[session_id])

class HistoryCreate(BaseModel):
    session_id: int
    result_id: int
    audio_id: int
    Edit_Action: str
    Original_Text: str
    Edited_Text : str
    
class EditText(BaseModel):
    session_id : int
    result_id : int
    audio_id : int
    Edited_Text : str
    
class EditEffect(BaseModel):
    session_id : int
    result_id : int
    audio_id : int    
    
    