from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserEdit(Base):
    __tablename__ = 'UserEdit'
    user_edit_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.user_id'))
    audio_id = Column(Integer, ForeignKey('AudioFile.audio_id'))
    result_id = Column(Integer, ForeignKey('Result.result_id'))
    Applied_Effect = Column(Boolean, nullable=False)
    
    # 1:N 관계 설정
    user = relationship("User")
    audio_file = relationship("AudioFile")
    result = relationship("Result")