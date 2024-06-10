from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import SessionLocal


async def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()


get_session = Annotated[AsyncSession, Depends(get_db_session)]
