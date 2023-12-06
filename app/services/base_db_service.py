from dataclasses import dataclass
from typing import Generic, TypeVar, Any

from sqlalchemy import select, Integer
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import db
from app.db.database import DefaultBase


ModelType = TypeVar("ModelType", bound=DefaultBase)


@dataclass
class BaseDBService(Generic[ModelType]):
    """Базовый класс операций с базой данных."""

    model: type[ModelType]
    db_session: db.session

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


class CRUDBase(object):
    """Базовый класс CRUD операций."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    @classmethod
    def get(cls, id_) -> db.Model:
        """Возвращает объект по id."""

        return db.session.execute(db.select(cls).filter_by(id=id_)).scalar_one_or_none()

    @classmethod
    def get_all(cls) -> list[db.Model]:
        return db.session.scalars(select(cls)).all()

    @classmethod
    def create(cls, **kwargs) -> db.Model:
        db_obj = cls(**kwargs)
        db.session.add(db_obj)
        db.session.commit()
        return cls.get(db_obj.id)

    @classmethod
    def update(cls, id_, **kwargs) -> db.Model:
        db_obj = cls.get(id_)
        for column, value in kwargs.items():
            setattr(db_obj, column, value)
        db.session.commit()
        return db_obj

    @classmethod
    def delete(cls, id_) -> str:
        db_obj = cls.get(id_)
        db.session.delete(db_obj)
        db.session.commit()
        return f"Запись '{db_obj}' удалена"
