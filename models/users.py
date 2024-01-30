from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from config.database import Base
from pydantic import BaseModel
from datetime import datetime

class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    login_id = Column(String(20))
    login_pw = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserLogin(BaseModel):
    login_id: str
    login_pw: str
    
class Usercreate(BaseModel):
    login_id: str
    login_pw: str

class UserinDB(Usercreate):
    created_at : datetime
    
class UserResponse(BaseModel):
    login_id: str
    created_at: datetime


