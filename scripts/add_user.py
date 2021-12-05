import config
from app import db
from app.login.models import User

# Create base users
u = User(username='admin', role=config.ROLE_ADMIN)
u.set_password('admin')
db.session.add(u)

u = User(username='user', role=config.ROLE_USER)
u.set_password('user')
db.session.add(u)

u = User(username='metod', role=config.ROLE_METOD)
u.set_password('metod')
db.session.add(u)

u = User(username='bibl', role=config.ROLE_BIBL)
u.set_password('bibl')
db.session.add(u)

db.session.commit()
