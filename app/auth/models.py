from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
from config import FlaskConfig as Config


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Integer(), default=Config.ROLE_METOD)

    def __repr__(self):
        return "{}".format(self.username)

    def get_role_id(self):
        return "{}".format(self.role)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
