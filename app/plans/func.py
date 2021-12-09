import requests
from config import ApeksAPI


def disciplines_comp_load(curriculum_discipline_id, competency_id):  # Загрузка связи дисциплины с компетенцией
    params = {'token': ApeksAPI.TOKEN}
    data = {'table': 'plan_curriculum_discipline_competencies',
            'fields[curriculum_discipline_id]': curriculum_discipline_id,
            'fields[competency_id]': competency_id}
    requests.post(ApeksAPI.URL + '/api/call/system-database/add', params=params, data=data)


def disciplines_comp_del(curriculum_discipline_id):  # Удаление связей дисциплины и компетенций
    params = {'token': ApeksAPI.TOKEN,
              'table': 'plan_curriculum_discipline_competencies',
              'filter[curriculum_discipline_id]': curriculum_discipline_id}
    requests.delete(ApeksAPI.URL + '/api/call/system-database/delete', params=params)


def disciplines_wp_clean(work_program_id):  # Удаление записей о компетенциях в РП
    params = {'token': ApeksAPI.TOKEN,
              'table': 'mm_work_programs_competencies_data',
              'filter[work_program_id]': work_program_id}
    requests.delete(ApeksAPI.URL + '/api/call/system-database/delete', params=params)
