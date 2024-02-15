from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from models.EffectSounds import EffectSound
from models.Results import Result
from config.database import get_db
from models.EffectSounds import EffectSoundCreate
from datetime import datetime
import pytz

router = APIRouter()



@router.post("/effects", status_code=200)
def create_effect_sound(effect_sound: EffectSoundCreate, db: Session = Depends(get_db)):
    # 새로운 효과음 후보 객체를 생성합니다.
    
    # 한국 시간대(KST, UTC+9)를 사용하여 'created_at'을 설정합니다.
    korea_time_zone = pytz.timezone("Asia/Seoul")
    created_at_kst = datetime.now(korea_time_zone)
    
    new_effect_sound = EffectSound(
        result_id=effect_sound.result_id,
        Effect_Name=effect_sound.Effect_Name,
        EffectFilePath=effect_sound.EffectFilePath,
        Upload_Date=created_at_kst
    )
    db.add(new_effect_sound)
    db.commit()
    db.refresh(new_effect_sound)
    return new_effect_sound