import logging

import discord
from sqlalchemy import Column, Integer, String, ForeignKey, delete, UniqueConstraint
from sqlalchemy.exc import IntegrityError
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
    tokens = relationship("FzToken", lazy="selectin", back_populates="user")


class FzToken(Base):
    __tablename__ = "fz_tokens"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    token_id = Column('token_id', String)
    user_id = Column(Integer, ForeignKey("fz_discord_users.id"))
    user = relationship("FzDiscordUser", back_populates="tokens", lazy="selectin")
    __table_args__ = (
        UniqueConstraint('user_id', 'token_id', name='_token_type_uc'),
    )


async def start_db():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def add_new_user(user: discord.Member, token, name: str):
    async with async_session() as session:
        db_user = FzDiscordUser(id=user.id, tokens=[FzToken(token_id=token, name=name)])
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
    logger.info(f"Added new user with id {user.id} and token {token} and name {name}")
    return True


async def append_token(user: discord.Member, token, name: str):
    async with async_session() as session:
        q = select(FzDiscordUser).where(FzDiscordUser.id == user.id)
        db_user = await session.scalar(q)
        if db_user is not None:
            try:
                db_user.tokens.append(FzToken(token_id=token, name=name))
                await session.commit()
                await session.refresh(db_user)
                logger.info(f"Added token: {token} with name: {name} to user {user.id} ")
                return True
            except IntegrityError:
                logger.info(f"User {user.id} already has token {token}")
                return False
        else:
            return await add_new_user(user, token, name)


async def remove_token(user: discord.Member, token: str):
    # check how many tokens the user has
    async with async_session() as session:
        q = delete(FzToken).where(FzToken.token_id == token, FzToken.user_id == user.id)
        result = await session.execute(q)
        await session.commit()
        if result.rowcount == 0:
            logger.info(f"User {user.id} does not have token {token}")
            return False
        else:
            logger.info(f"Removed token {token} from user {user.id}")
            return True


async def get_tokens(user: discord.Member) -> list[FzToken]:
    async with async_session() as session:
        q = select(FzDiscordUser).where(FzDiscordUser.id == user.id)
        db_user = await session.scalar(q)
        if db_user is not None and len(db_user.tokens) > 0:
            return db_user.tokens
        else:
            return []


async def get_all_data():
    async with async_session() as session:
        q = select(FzDiscordUser)
        users = await session.execute(q)
        users = users.scalars()
        unpacked_users = []
        for user in users:
            unpacked_users.append(
                {'id': user.id, 'tokens': [{"id": token.token_id, "name": token.name} for token in user.tokens]})
        return unpacked_users
