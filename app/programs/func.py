from app.main.func import db_filter_req


def plan_department_disciplines(education_plan_id, department_id):
    """
    Getting department disciplines info as dict
    (disc_ID:[disc_code:disc_name]).
    """
    disciplines = {}
    resp = db_filter_req(
        "plan_curriculum_disciplines", "education_plan_id", education_plan_id
    )
    for disc in resp:
        if disc["level"] == "3" and disc["department_id"] == str(
                department_id
        ):
            disciplines[disc["id"]] = [
                disc["code"],
                db_filter_req(
                    "plan_disciplines",
                    "id",
                    disc["discipline_id"]
                )[0]["name"],
            ]
    return disciplines
