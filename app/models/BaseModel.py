from typing import List, Dict

from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

from app.core import Base


class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=func.now(), server_default=func.now(), nullable=False)
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now(), server_default=func.now(),
                         server_onupdate=func.now(),
                         nullable=False)

    @staticmethod
    def extra_relationships(model_name: str, model, relationship_un_selects: Dict[str, List[str]]):
        result = {}
        for column in model.__table__.columns:
            if (not relationship_un_selects or model_name not in relationship_un_selects or column.name
                    not in relationship_un_selects[model_name]):
                result[column.name] = getattr(model, column.name)
        return result

    def dict(self, un_selects: List[str] = None, relationship_un_selects=None,
             relationships: List[str] = None):
        result = {}
        # Get the values of the columns
        for column in self.__table__.columns:
            if not un_selects or column.name not in un_selects:
                result[column.name] = getattr(self, column.name)

        # Take the value of relationships if appointed
        if relationships:
            for relationship_name in relationships:
                if hasattr(self, relationship_name):
                    value = getattr(self, relationship_name)
                    if value is not None:
                        if isinstance(value, list):
                            result[relationship_name] = [
                                self.extra_relationships(model_name=relationship_name, model=item,
                                                         relationship_un_selects=relationship_un_selects) for item in
                                value]
                        else:
                            result[relationship_name] = self.extra_relationships(model_name=relationship_name,
                                                                                 model=value,
                                                                                 relationship_un_selects=relationship_un_selects)

        return result
