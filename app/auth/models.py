from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from config import FlaskConfig

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Integer(), default=FlaskConfig.ROLE_METOD)

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


def init_db():
    db.create_all()

    u = User(username='admin', role=FlaskConfig.ROLE_ADMIN)
    u.set_password('admin')
    db.session.add(u)

    u = User(username='user', role=FlaskConfig.ROLE_USER)
    u.set_password('user')
    db.session.add(u)

    u = User(username='metod', role=FlaskConfig.ROLE_METOD)
    u.set_password('metod')
    db.session.add(u)

    u = User(username='bibl', role=FlaskConfig.ROLE_BIBL)
    u.set_password('bibl')
    db.session.add(u)

    db.session.commit()