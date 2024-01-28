from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker

# DatabaseURL = 'mysql+aiomysql://root:1234@localhost:3306/test'
DatabaseURL = 'mysql+aiomysql://root:1234@localhost:3306/test'
engine = create_async_engine(DatabaseURL, echo = True)

# 비동기 세션을 위한 설정
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

Base: DeclarativeMeta = declarative_base()


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()