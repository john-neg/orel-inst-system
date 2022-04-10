from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from config import FlaskConfig, DbRoles

app = Flask(__name__)
app.config.from_object(FlaskConfig)
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Integer(), default=DbRoles.ROLE_METOD)

    def __repr__(self):
        return "{}".format(self.username)

    def get_role_id(self):
        return "{}".format(self.role)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


db.create_all()

# Create base users

u = User(username='admin', role=DbRoles.ROLE_ADMIN)
u.set_password('admin')
db.session.add(u)

u = User(username='user', role=DbRoles.ROLE_USER)
u.set_password('user')
db.session.add(u)

u = User(username='metod', role=DbRoles.ROLE_METOD)
u.set_password('metod')
db.session.add(u)

u = User(username='bibl', role=DbRoles.ROLE_BIBL)
u.set_password('bibl')
db.session.add(u)

db.session.commit()
