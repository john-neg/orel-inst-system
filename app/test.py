from app.classes import ApeksStaff

department_id = '22'
staff_id = '122'



print(ApeksStaff.staff[str(department_id)][str(staff_id)]['specialRank'] is None)