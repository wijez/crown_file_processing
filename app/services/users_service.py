from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.crud import crud_user
from app.core import get_settings, Config
from app.schemas import UserCreateSchema, UserUpdateSchema

settings = get_settings()

logger = Config.setup_logging()


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: UserCreateSchema):
        logger.info("Service: create_user called")
        user_email = await crud_user.get(self.session, User.email == user.email)
        user_name = await crud_user.get(self.session, User.full_name == user.username)
        if user_email:
            logger.error("Service: error email already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="email already exists"
            )
        if user_name:
            logger.error("Service: error username already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="username already exists"
            )
        result = await crud_user.create(self.session, user)
        logger.info("Service: create_user called successfully!")
        return result

    async def update_user(self, user: UserUpdateSchema, user_id: int):
        logger.info("Service: update_user called")
        user_by_id = await crud_user.find_one_by_id(user_id, self.session)
        if not user_by_id:
            logger.error("Service: update_user error invalid user id")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )

        result = await crud_user.update(self.session, obj_in=user, db_obj=user_by_id)
        logger.info("Service: update_user called successfully")
        return result

    async def get_list_user(self, limit: int, offset: int):
        logger.info("Service: get_list_user called")
        result = await crud_user.get_multi(self.session, limit=limit, offset=offset)
        logger.info("Service: get_list_user called successfully!")
        return result

    async def delete_user(self, user_id: int):
        logger.info("Service: delete_user called")
        user_delete = await crud_user.get(self.session, User.id == user_id)
        if not user_delete:
            logger.error("Service: delete_user error user id not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="id user not found"
            )

        result = await crud_user.delete(self.session, user_id)
        logger.info("Service: delete_user called successfully!")
        return result

    async def get_one_by_id(self, user_id: int):
        logger.info("Service: get_one_by_id called")
        user = await crud_user.get(self.session, User.id == user_id)
        if not user:
            logger.error("Service: delete_user error user id not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="id user not found"
            )

        logger.info("Service: get_one_by_id called successfully!")
        return user
