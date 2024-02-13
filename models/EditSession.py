from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EditSession(Base):
    __tablename__ = 'editsession'
    session_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    audio_id = Column(Integer, ForeignKey('audiofile.audio_id'))
    Last_Edit_result_id = Column(Integer, ForeignKey('result.result_id'), nullable=True)
    Start_Edit = Column(DateTime, nullable=False)
    End_Edit = Column(DateTime, nullable=True)
    Session_State = Column(String(50), nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="editsession")
    audiofile = relationship("AudioFile", back_populates="editsession")
    edithistory = relationship("EditHistory", back_populates="session")

class SessionResponse(BaseModel):
    session_id : int
    user_id : int
    audio_id : int
    Last_Edit_result_id: Optional[int] = None
    Start_Edit : datetime
    Session_State : str
    
class SessionCreate(BaseModel):
    audio_id: int

class SessionUpdate(BaseModel):
    Last_Edit_result_id: Optional[int] = None

class SessionPause(BaseModel):
    session_id : int
    End_Edit : datetime
    Session_State : str
    Last_Edit_result_id: Optional[int] = None