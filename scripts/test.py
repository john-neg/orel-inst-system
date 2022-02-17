from app.auth.models import User

# from app.func import *
# department_id = '12'
# staff_id = '32'
# month = '12'
# year = '2021'
#
# lessons_xlsx_exp(department_id, staff_id, month, year)
# lessons_ical_exp(department_id, staff_id, month, year)

users = User.query.all()
print(users)