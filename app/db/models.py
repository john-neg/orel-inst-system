from typing import Any

from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash

from app.db.database import Base
from config import FlaskConfig


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True)
    password_hash = Column(String(128))
    role = Column(Integer(), default=FlaskConfig.ROLE_METOD)

    def __init__(self, username=None, role=None, *args: Any,
                 **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.username = username
        self.role = role

    def __repr__(self):
        return "{}".format(self.username)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_role_id(self):
        return "{}".format(self.role)

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`") from None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
