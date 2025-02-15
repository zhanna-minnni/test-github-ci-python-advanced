from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models import Base

DATABASE_URL = "sqlite+aiosqlite:///./recipes.db"
engine = create_async_engine(DATABASE_URL, echo=True)

async_session: sessionmaker[AsyncSession] = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
