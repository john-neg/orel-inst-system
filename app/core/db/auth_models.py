from functools import total_ordering

from flask_login import AnonymousUserMixin, UserMixin
from sqlalchemy import String, ForeignKey, Integer, UniqueConstraint
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
    permissions: Mapped[list["UsersPermissions"]] = relationship(
        "UsersPermissions",
        secondary="users_roles_permissions",
        back_populates="roles",
    )

    def __repr__(self):
        return self.name


@total_ordering
class UsersPermissions(db.Model):
    """Модель прав доступа пользователей."""

    __tablename__ = "users_permissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    roles: Mapped[list["UsersRoles"]] = relationship(
        "UsersRoles",
        secondary="users_roles_permissions",
        back_populates="permissions",
    )

    def __repr__(self):
        return self.slug

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.name < other.name
        return NotImplemented


class UsersRolesPermissions(db.Model):
    """Модель соотношения ролей и прав доступа."""

    __tablename__ = "users_roles_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id"),)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("users_roles.id"),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("users_permissions.id"),
        primary_key=True,
    )


class AnonymousUser(AnonymousUserMixin):
    """Модель неавторизованного пользователя."""

    def role(self):
        return
