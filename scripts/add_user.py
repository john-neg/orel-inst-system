from config import DbRoles
from app import db
from app.auth.models import User

# Create base users
# u = User(username='admin', role=DbRoles.ROLE_ADMIN)
# u.set_password('admin')
# db.session.add(u)
#
# u = User(username='user', role=DbRoles.ROLE_USER)
# u.set_password('user')
# db.session.add(u)
#
# u = User(username='metod', role=DbRoles.ROLE_METOD)
# u.set_password('metod')
# db.session.add(u)

# u = User(username='bibl', role=DbRoles.ROLE_BIBL)
# u.set_password('bibl')
# db.session.add(u)
#
# db.session.commit()
u = User(username='test')
db.session.add(u)
print(u)