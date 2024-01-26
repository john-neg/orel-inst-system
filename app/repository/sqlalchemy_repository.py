from dataclasses import dataclass
from typing import TypeVar, Any, Generic

import flask_sqlalchemy.session
from flask import request
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from config import FlaskConfig
from .abstract_repository import AbstractDBRepository
from ..db.database import DefaultBase
from ..db.database import db


ModelType = TypeVar("ModelType", bound=DefaultBase)


@dataclass
class DbRepository(Generic[ModelType], AbstractDBRepository):
    """Базовый класс операций с базой данных."""

    model: type[ModelType]
    db_session: flask_sqlalchemy.session

    def list(self, **kwargs: Any) -> list[ModelType]:
        """Выводит список всех объектов модели базы данных."""

        statement = select(self.model).filter_by(**kwargs)
        result = self.db_session.execute(statement)
        objs: list[ModelType] = result.scalars().all()
        return objs

    def get(self, **kwargs: Any) -> ModelType:
        """Возвращает один объект соответствующий параметрам запроса."""

        statement = select(self.model).filter_by(**kwargs)
        result = self.db_session.execute(statement)
        try:
            obj: ModelType = result.scalar_one()
            return obj
        except NoResultFound:
            pass

    def create(self, **kwargs: Any) -> ModelType:
        """Создает объект базы данных."""

        db_obj: ModelType = self.model(**kwargs)
        self.db_session.add(db_obj)
        self.db_session.commit()
        return self.get(id=db_obj.id)

    def update(self, id_: int, **kwargs) -> ModelType:
        """Обновляет объект базы данных."""

        db_obj = self.get(id=id_)
        for column, value in kwargs.items():
            setattr(db_obj, column, value)
        self.db_session.commit()
        return db_obj

    def delete(self, id_: int) -> str:
        """Удаляет объект базы данных."""

        db_obj = self.get(id=id_)
        self.db_session.delete(db_obj)
        self.db_session.commit()
        return f"Запись {self.model.__name__.lower()} удалена"

    def paginated(self, **kwargs: Any) -> Pagination:
        """Возвращает Pagination объект содержащий объекты модели."""

        page = request.args.get("page", 1, type=int)
        paginated_data = db.paginate(
            select(self.model).filter_by(**kwargs),
            page=page,
            per_page=FlaskConfig.ITEMS_PER_PAGE,
            error_out=True,
        )
        return paginated_data
