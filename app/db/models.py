from flask_login import AnonymousUserMixin, UserMixin
from sqlalchemy.future import select
from werkzeug.security import generate_password_hash, check_password_hash

from app.db.database import db


class User(db.Model, UserMixin):
    """Модель пользователя."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey("users_roles.id"), nullable=False)
    role = db.relationship("UserRoles", back_populates="user", lazy='subquery')

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
        user = db.session.get(User, user_id)
        db.session.delete(user)
        db.session.commit()



class UserRoles(db.Model):
    """Модель ролей пользователей."""

    __tablename__ = "users_roles"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    user = db.relationship("User", back_populates="role")

    def __repr__(self):
        return self.name

    @staticmethod
    def available_roles():
        return db.session.scalars(select(UserRoles)).all()

    @staticmethod
    def get_by_slug(slug):
        return db.session.execute(
            select(UserRoles).filter_by(slug=slug)
        ).scalar_one()


class AnonymousUser(AnonymousUserMixin):
    """Модель неавторизованного пользователя."""

    def role(self):
        return
