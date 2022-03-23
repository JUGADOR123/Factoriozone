import logging

import discord
from sqlalchemy import Column, Integer, String, ForeignKey, delete, UniqueConstraint
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

database_url = "sqlite+aiosqlite:///./data.db"
engine = create_async_engine(database_url, future=True, echo=True)
async_session = sessionmaker(bind=engine, future=True, class_=AsyncSession)
Base = declarative_base()

logger = logging.getLogger(__name__)


class FzDiscordUser(Base):
    __tablename__ = "fz_discord_users"
    id = Column(Integer, primary_key=True)
    tokens = relationship("FzToken", lazy="selectin")


class FzToken(Base):
    __tablename__ = "fz_tokens"
    id = Column(Integer, primary_key=True)
    token_id = Column(String)
    parent_id = Column(Integer, ForeignKey("fz_discord_users.id"))
    __table_args__ = (
        UniqueConstraint('parent_id', 'token_id', name='_token_type_uc'),
    )


async def start_db():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def add_new_user(user: discord.Member, token):
    async with async_session() as session:
        db_user = FzDiscordUser(id=user.id, tokens=[FzToken(token_id=token)])
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
    logger.info(f"Added new user with id {user.id} and token {token}")
    return True


async def append_token(user: discord.Member, token):
    async with async_session() as session:
        q = select(FzDiscordUser).where(FzDiscordUser.id == user.id)
        db_user = await session.execute(q)
        db_user = db_user.scalar()
        if db_user is not None:
            db_user.tokens.append(FzToken(token_id=token))
            await session.commit()
            await session.refresh(db_user)
            logger.info(f"Added token {token} to user {user.id}")
            return True
        else:
            return await add_new_user(user, token)


async def remove_token(user: discord.Member, token: str):
    # check how many tokens the user has
    async with async_session() as session:
        db_user = await session.get(FzDiscordUser, id=user.id)
        if db_user is not None and len(db_user.tokens) > 1:
            await session.execute(delete(FzToken).where(FzToken.token_id == token, FzToken.parent_id == user.id))
            await session.commit()
            await session.refresh(db_user)
            logger.info(f"Removed token {token} from user {user.id}")
            return True
        elif db_user is not None and len(db_user.tokens) == 1:
            await session.execute(delete(FzDiscordUser).where(FzDiscordUser.id == user.id))
            await session.commit()
            logger.info(f"Removed user {user.id} as they only had one token")
            return True
        else:
            logger.info(f"User {user.id} does not exist")
            return False


async def get_all_data():
    async with async_session() as session:
        q = select(FzDiscordUser)
        users = await session.execute(q)
        users = users.scalars()
        unpacked_users = []
        for user in users:
            unpacked_users.append({'id': user.id, 'tokens': [token.token_id for token in user.tokens]})
        return unpacked_users
