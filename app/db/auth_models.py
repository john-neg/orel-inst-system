from flask_login import AnonymousUserMixin, UserMixin
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import db


class Users(db.Model, UserMixin):
    """Модель пользователя."""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    role_id: Mapped[int] = mapped_column(ForeignKey("users_roles.id"), nullable=False)
    role: Mapped["UsersRoles"] = relationship(
        "UsersRoles", back_populates="user", lazy="immediate"
    )

    def __repr__(self):
        return self.username


class UsersRoles(db.Model):
    """Модель ролей пользователей."""

    __tablename__ = "users_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    user: Mapped[list["UsersRoles"]] = relationship("Users", back_populates="role")

    def __repr__(self):
        return self.name


class AnonymousUser(AnonymousUserMixin):
    """Модель неавторизованного пользователя."""

    def role(self):
        return
