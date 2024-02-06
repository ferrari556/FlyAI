from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class EditHistory(Base):
    __tablename__ = 'EditHistory'
    history_id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('EditSession.session_id'))
    result_id = Column(Integer, ForeignKey('Result.result_id'))
    Edit_Action = Column(String(30), nullable=False)
    Original_Text = Column(String(255), nullable=False)
    Edited_Text = Column(String(255), nullable=False)
    EditDate = Column(DateTime, nullable=False)
    
    
    # 1:N 관계 설정
    # edit_session = relationship("EditSession")
    result = relationship("Result")
    edit_session = relationship('EditSession', foreign_keys=[session_id])
    