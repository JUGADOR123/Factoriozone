import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String

database_url = "sqlite+aiosqlite:///./data.db"
engine = create_async_engine(database_url, future=True, echo=True)
async_session = sessionmaker(bind=engine, future=True, class_=AsyncSession)
Base = declarative_base()

logger = logging.getLogger(__name__)


class FzTokens(Base):
    __tablename__ = "fz_tokens"

    user_id = Column(Integer, primary_key=True)
    token = Column(String(100), nullable=False)


async def start_db():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def add_token(user_id, token):
    async with async_session() as session:
        await session.add(FzTokens(user_id=user_id, token=token))
        await session.commit()
        logger.info(f"Added token for user {user_id}")