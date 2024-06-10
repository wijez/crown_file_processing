from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self._model = model

    async def create(
            self, session: AsyncSession, obj_in: CreateSchemaType
    ) -> ModelType:
        db_obj = self._model(**obj_in.dict())
        session.add(db_obj)
        await session.commit()
        return db_obj

    async def get(self, session: AsyncSession, *args, **kwargs) -> Optional[ModelType]:
        result = await session.execute(
            select(self._model).filter(*args).filter_by(**kwargs)
        )
        return result.scalars().first()

    async def get_multi(
            self, session: AsyncSession, *args, offset: int = 0, limit: int = 100, **kwargs
    ) -> List[ModelType]:
        result = await session.execute(
            select(self._model)
            .filter(*args)
            .filter_by(**kwargs)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all(
            self, session: AsyncSession, *args, **kwargs
    ) -> List[ModelType]:
        result = await session.execute(
            select(self._model)
            .filter(*args)
            .filter_by(**kwargs)
        )
        return result.scalars().all()

    async def count_all(
            self, session: AsyncSession, *args, **kwargs
    ) -> int:
        query = select(func.count()).select_from(self._model).filter(*args).filter_by(**kwargs)
        result = await session.execute(query)
        return result.scalar_one()

    async def update(
            self,
            session: AsyncSession,
            *,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]],
            db_obj: Optional[ModelType] = None,
            **kwargs
    ) -> Optional[ModelType]:
        db_obj = db_obj or await self.get(session, **kwargs)
        if db_obj is not None:
            obj_data = db_obj.dict()
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            session.add(db_obj)
            await session.commit()
        return db_obj

    async def delete(
            self, session: AsyncSession, *args, db_obj: Optional[ModelType] = None, **kwargs
    ) -> ModelType:
        db_obj = db_obj or await self.get(session, *args, **kwargs)
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def create_bulk(
            self, session: AsyncSession, objs_in: List[CreateSchemaType]
    ) -> List[ModelType]:
        db_objs = [self._model(**obj_in.dict()) for obj_in in objs_in]
        session.add_all(db_objs)
        await session.commit()
        return db_objs

    async def update_bulk(
            self,
            session: AsyncSession,
            objs_in: List[UpdateSchemaType],
            db_objs: Optional[List[ModelType]] = None,
    ) -> List[ModelType]:
        db_objs = db_objs or await self.get_multi(session)
        if len(objs_in) != len(db_objs):
            raise ValueError("Input and existing objects count mismatch")

        for i, db_obj in enumerate(db_objs):
            obj_data = db_obj.dict()
            update_data = objs_in[i].dict(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])

        await session.commit()
        return db_objs

    async def delete_bulk(self, session: AsyncSession, db_objs: Optional[List[ModelType]] = None):
        db_objs = db_objs or await self.get_multi(session)
        for obj in db_objs:
            await session.delete(obj)  # Assuming self.delete is your method for deleting individual objects.
        await session.commit()
