import requests
from config import FlaskConfig as Config
from config import ApeksConfig as Apeks


def allowed_file(filename):
    """Check if file extension in allowed list in Config."""
    return (
            "." in filename and filename.rsplit(".", 1)[1] in Config.ALLOWED_EXTENSIONS
    )


def db_request(table_name):
    """DB request function without filter."""
    params = {"token": Apeks.TOKEN, "table": table_name}
    response = requests.get(
        Apeks.URL + "/api/call/system-database/get", params=params
    )
    return response.json()["data"]


def db_filter_req(table_name, sql_field, sql_value):
    """Filtered DB request (DB table, filter, value)."""
    params = {
        "token": Apeks.TOKEN,
        "table": table_name,
        "filter[" + sql_field + "]": str(sql_value),
    }
    response = requests.get(
        Apeks.URL + "/api/call/system-database/get", params=params
    )
    return response.json()["data"]


def education_specialty():
    """Getting education_speciality data."""
    payload = {"token": Apeks.TOKEN, "table": "plan_education_specialties"}
    request = requests.get(
        Apeks.URL + "/api/call/system-database/get", params=payload
    )
    specialties = {}
    for i in request.json()["data"]:
        specialties[i.get("id")] = i.get("name")
    return specialties


def education_plans(education_specialty_id, year=0):
    """Getting education plans with selected speciality."""
    payload = {
        "token": Apeks.TOKEN,
        "table": "plan_education_plans",
        "filter[data_type]": "plan",
        "filter[education_specialty_id]": education_specialty_id,
        "filter[active]": "1",
    }
    request = requests.get(
        Apeks.URL + "/api/call/system-database/get", params=payload
    )
    plans = {}
    if year == 0:
        for i in request.json()["data"]:
            plans[i.get("id")] = i.get("name")
        return plans
    else:
        for i in request.json()["data"]:
            if i.get("custom_start_year") == year:
                plans[i.get("id")] = i.get("name")
            elif i.get("custom_start_year") is None:
                date = db_filter_req(
                            "plan_semesters", "education_plan_id", i.get("id")
                        )
                if date[0]["start_date"].split("-")[0] == year:
                    plans[i.get("id")] = i.get("name")
        return plans


def plan_curriculum_disciplines(education_plan_id):
    """Getting plan disciplines info as dict (disc_ID:[disc_code:disc_name])."""

    def disc_name(discipline_id):
        for discipline in disc_list:
            if discipline.get("id") == discipline_id:
                return discipline["name"]

    disciplines = {}
    disc_list = db_request("plan_disciplines")
    plan_disc = db_filter_req(
        "plan_curriculum_disciplines", "education_plan_id", education_plan_id
    )
    for disc in plan_disc:
        if (
                disc["level"] == "3" and not disc["type"] == "16"
        ):  # type 16 - группы дисциплин
            disciplines[disc["id"]] = [disc["code"], disc_name(disc["discipline_id"])]
    return disciplines


def xlsx_iter_rows(ws):
    """Reading imported XLSX file row by row."""
    for row in ws.iter_rows():
        yield [cell.value for cell in row]


def xlsx_normalize(worksheet, replace_dict):
    """Function to replace symbols in table."""
    for key, val in replace_dict.items():
        for r in range(1, worksheet.max_row + 1):
            for c in range(1, worksheet.max_column + 1):
                s = str(worksheet.cell(r, c).value)
                worksheet.cell(r, c).value = s.replace(key, val)
    return worksheet


def get_system_user_name(user_id):
    """Get name of system user by ID."""
    resp = db_filter_req("state_staff", "user_id", user_id)
    if resp:
        return f'{resp[0]["family_name"]} {resp[0]["name"][0]}.{resp[0]["surname"][0]}.'
    else:
        return "Пользователь не существует"


def add_wp_field(work_program_id, field_id):
    """Добавление пустых полей в рабочую программу в случае их отсутствия."""
    params = {"token": Apeks.TOKEN}
    data = {
        "table": "mm_work_programs_data",
        "fields[work_program_id]": work_program_id,
        "fields[field_id]": field_id,
        "fields[data]": "",
    }
    requests.post(
        Apeks.URL + "/api/call/system-database/add", params=params, data=data
    )
