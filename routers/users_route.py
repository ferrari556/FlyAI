from models.users import User, Usercreate, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from config.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from services import login_service
from services.login_service import oauth2_scheme

router = APIRouter()

# ID로 사용자 읽기
@router.get("/users/{user_id}", tags=["Users"])
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(e)})

@router.get("/auth/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}

# 사용자 생성
@router.post("/signup", tags=["Users"], response_model = UserResponse)
async def signup(user: Usercreate, db: AsyncSession = Depends(get_db)):
    try:
        db_user = await login_service.create_user(db, user)
        
        return {
            "login_id": db_user.login_id,
            "login_pw": db_user.login_pw,
            "created_at": db_user.created_at,
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    db_user = await login_service.authenticate_user(db, form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = login_service.create_access_token({"sub": db_user.login_id})
    return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/login")
# async def login(user: Usercreate, db: AsyncSession = Depends(get_db)):
#     try:
#         db_user = await login_service.authenticate_user(db, user.login_id, user.login_pw)
#     except Exception as e:
#         raise HTTPException(status_code=401, detail=str(e))

#     access_token = login_service.create_access_token({"sub": db_user.login_id})
#     return {"login_id": db_user.login_id, "access_token": access_token}

    