from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import Mapped

db = SQLAlchemy()


class CRUDBase(object):
    """Базовый класс CRUD операций."""

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get(cls, id_) -> db.Model:
        """Возвращает объект по id."""

        return db.session.execute(select(cls).where(cls.id == id_)).scalar_one_or_none()

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
