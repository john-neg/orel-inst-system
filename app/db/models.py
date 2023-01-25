from flask_login import AnonymousUserMixin, UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app.db.database import Base, session


class User(Base, UserMixin):
    """Модель пользователя."""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True)
    password_hash = Column(String(128))
    role_id = Column(Integer, ForeignKey("users_roles.id"), nullable=False)
    role = relationship("UserRoles", back_populates="user")

    def __repr__(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def add_user(username, password, role_id):
        new_user = User(username=username, role_id=role_id)
        new_user.set_password(password)
        session.add(new_user)
        session.commit()
        return new_user

    def edit_user(self, username, password, role_id):
        self.username = username
        if password:
            self.set_password(password)
        self.role_id = role_id
        session.commit()

    @staticmethod
    def delete_user(user_id):
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()


class UserRoles(Base):
    """Модель ролей пользователей."""

    __tablename__ = "users_roles"
    id = Column(Integer, primary_key=True)
    slug = Column(String(10), nullable=False, unique=True)
    name = Column(String(64), nullable=False, unique=True)
    user = relationship("User", back_populates="role")

    def __repr__(self):
        return self.name

    @staticmethod
    def available_roles():
        return session.scalars(select(UserRoles)).all()

    @staticmethod
    def get_by_slug(slug):
        return session.execute(
            select(UserRoles).filter_by(slug=slug)
        ).scalar_one()


class AnonymousUser(AnonymousUserMixin):
    """Модель неавторизованного пользователя."""

    def role(self):
        return
