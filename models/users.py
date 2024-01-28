from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    login_id = Column(String(20))
    login_pw = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())



