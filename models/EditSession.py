from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EditSession(Base):
    __tablename__ = 'EditSession'
    session_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.user_id'))
    audio_id = Column(Integer, ForeignKey('AudioFile.audio_id'))
    Start_Edit = Column(DateTime, nullable=False)
    End_Edit = Column(DateTime, nullable=True)
    Session_State = Column(String(50), nullable=False)
    last_edit_history_id = Column(Integer, ForeignKey('EditHistory.history_id'), nullable=True)
    
    # 1:N 관계 설정
    user = relationship("User")
    audio_file = relationship("AudioFile")
    edit_history = relationship("EditHistory", foreign_keys=[last_edit_history_id])
    
    
class SessionResponse(BaseModel):
    session_id : int
    Start_Edit : datetime
    Session_State : str
    
class SessionCreate(BaseModel):
    audio_id: int

class SessionUpdate(BaseModel):
    last_edit_history: int

class SessionPause(BaseModel):
    session_id : int
    End_Edit : datetime
    Session_State : str
    last_edit_history : int