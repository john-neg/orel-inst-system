from __future__ import annotations

from app.common.classes.EducationPlan import EducationPlanWorkPrograms
from app.common.exceptions import ApeksParameterNonExistException
from app.common.func.api_post import work_program_add_parameter
from app.common.func.app_core import work_program_get_parameter_info


async def work_program_view_data(
        plan: EducationPlanWorkPrograms, parameter: str
) -> dict:
    """
    Возвращает список параметров рабочих программ плана.
    Если параметра нет в рабочей программе создает его.

    Parameters
    ----------
        plan: EducationPlanWorkPrograms
            экземпляр класса EducationPlanWorkProgram
        parameter: str
            параметр поля рабочей программы значение которого нужно вернуть

    Returns
    -------
        dict
            значение параметра для дисциплины
            {"Название дисциплины плана": {work_program_id: "Значение параметра"}}
    """
    programs_info = {}
    for disc in plan.disc_wp_match:
        disc_name = plan.discipline_name(disc)
        programs_info[disc_name] = {}
        if not plan.disc_wp_match[disc]:
            programs_info[disc_name]["none"] = "-->Программа отсутствует<--"
        else:
            for wp in plan.disc_wp_match[disc]:
                try:
                    field_data = work_program_get_parameter_info(
                        plan.work_programs_data[wp], parameter
                    )
                except ApeksParameterNonExistException:
                    await work_program_add_parameter(
                        wp, parameter
                    )
                    field_data = ""
                else:
                    field_data = "" if not field_data else field_data
                programs_info[disc_name][wp] = field_data
    return programs_info
