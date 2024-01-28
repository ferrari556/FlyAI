from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EditHistory(Base):
    __tablename__ = 'EditHistory'
    history_id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('EditSession.session_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    ChangeContent = Column(Text)
    ChangeTime = Column(DateTime)
    
    # 1:N 관계 설정
    edit_session = relationship("EditSession")
    user = relationship("User")