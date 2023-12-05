from flask_login import AnonymousUserMixin, UserMixin
from sqlalchemy import select, String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.db.database import db


class Users(db.Model, UserMixin):
    """Модель пользователя."""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    role_id: Mapped[int] = mapped_column(ForeignKey("users_roles.id"), nullable=False)
    role: Mapped["UsersRoles"] = relationship(
        "UsersRoles",
        back_populates="user",
        lazy='immediate'
    )

    def __repr__(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def add_user(username, password, role_id):
        new_user = Users(username=username, role_id=role_id)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def edit_user(self, username, password, role_id):
        self.username = username
        if password:
            self.set_password(password)
        self.role_id = role_id
        db.session.commit()

    @staticmethod
    def delete_user(user_id):
        user = db.session.get(Users, user_id)
        db.session.delete(user)
        db.session.commit()


class UsersRoles(db.Model):
    """Модель ролей пользователей."""

    __tablename__ = "users_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    user: Mapped[list["UsersRoles"]] = relationship("Users", back_populates="role")

    def __repr__(self):
        return self.name

    @staticmethod
    def available_roles():
        return db.session.scalars(select(UsersRoles)).all()

    @staticmethod
    def get_by_slug(slug):
        return db.session.execute(
            select(UsersRoles).filter_by(slug=slug)
        ).scalar_one()


class AnonymousUser(AnonymousUserMixin):
    """Модель неавторизованного пользователя."""

    def role(self):
        return
