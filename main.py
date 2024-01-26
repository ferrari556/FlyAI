from fastapi import FastAPI
from sqlalchemy import create_engine
from config.database import engine
from server.index import setup_cors
import uvicorn
from models.AudioFiles import Base as AudioFiles 
from models.EditHistory import Base as EditHistory 
from models.EditSession import Base as EditSession  
from models.Effectsounds import Base as Effectsounds  
from models.STTdata import Base as STTdata  
from models.UserEdits import Base as UserEdits  
from models.UserSoundEffects import Base as UserSoundEffects  
from models.users import Base as users  
from routers import (
    AudioFiles_route,
    EditHistory_route,
    EditSession_route,
    Effectsounds_route,
    STTdata_route,
    UserEdits_route,
    UserSoundEffects_route,
    users_route
)

# 초기 데이터베이스 연결
DatabaseURL = 'mysql+pymysql://root:1234@localhost:3306/test'
engine = create_engine(DatabaseURL)

app = FastAPI()

# API 암호화
setup_cors(app)

# 원하는 데이터베이스 생성
AudioFiles.metadata.create_all(bind=engine)
EditHistory.metadata.create_all(bind=engine)
EditSession.metadata.create_all(bind=engine)
Effectsounds.metadata.create_all(bind=engine)
STTdata.metadata.create_all(bind=engine)
UserEdits.metadata.create_all(bind=engine)
UserSoundEffects.metadata.create_all(bind=engine)
users.metadata.create_all(bind=engine)

# Prefix는 엔드포인트를 정할 때 사용
app.include_router(AudioFiles_route.router, prefix="", tags=["AudioFiles"])
app.include_router(EditHistory_route.router, prefix="", tags=["EditHistory"])
app.include_router(EditSession_route.router, prefix="", tags=["EditSession"])
app.include_router(Effectsounds_route.router, prefix="", tags=["Effectsounds"])
app.include_router(STTdata_route.router, prefix="", tags=["STTdata"])
app.include_router(UserEdits_route.router, prefix="", tags=["UserEdits"])
app.include_router(UserSoundEffects_route.router, prefix="", tags=["UserSoundEffects"])
app.include_router(users_route.router, prefix="", tags=["Users"])

@app.get('/')
def home():
    return {'msg' : 'Main'}

if __name__ == "__main__":
    uvicorn.run("main:app", host = "127.0.0.1", port = 8000, reload = True)

