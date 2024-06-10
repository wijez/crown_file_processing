from typing import Optional

from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.crud import CRUDBase
from app.schemas import UserSchema, UserCreateSchema, UserUpdateSchema


class CRUDUser(CRUDBase[UserSchema, UserCreateSchema, UserUpdateSchema]):
    async def find_one_by_id(self, id: int, session: AsyncSession) -> Optional[User]:
        return await self.get(session, User.id == id)

    async def find_one_by_username(self, username: str, session: AsyncSession) -> Optional[User]:
        return await self.get(session, User.username == username)

    async def find_one_by_email(self, email: str, session: AsyncSession) -> Optional[User]:
        return await self.get(session, User.email == email)

    async def create_one(self, schema: UserCreateSchema, session: AsyncSession):
        return await self.create(session=session, obj_in=schema)

    @staticmethod
    async def update_token_version(session: AsyncSession, id: int, token_version: int):
        query = sql_update(User).where(
            User.id == id).values(token_version=token_version).execution_options(
            synchronize_session="fetch")
        await session.execute(query)
        await session.commit()


crud_user = CRUDUser(User)
