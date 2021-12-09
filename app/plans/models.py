import pandas as pd
import requests
from numpy import matrix
from app.main.func import db_filter_req
from app.plans.func import disciplines_wp_clean, disciplines_comp_del
from config import ApeksAPI


class EducationPlan:
    def __init__(self, education_plan_id):
        self.education_plan_id = education_plan_id
        self.disciplines = self.disciplines_list()
        self.competencies = self.get_comp()

    def disciplines_list(self):  # Получение списка ID, кодов и названий дисциплин плана
        disciplines = {}
        for disc in db_filter_req('plan_curriculum_disciplines', 'education_plan_id', self.education_plan_id):
            if disc['level'] == '3':
                disciplines[disc['id']] = [disc['code'],
                                           db_filter_req('plan_disciplines', 'id', disc['discipline_id'])[0]['name']]
        return disciplines

    def discipline_name(self, curriculum_discipline_id):
        return f'{self.disciplines[str(curriculum_discipline_id)][0]} {self.disciplines[str(curriculum_discipline_id)][1]}'

    def get_comp(self):
        return db_filter_req('plan_competencies', 'education_plan_id', self.education_plan_id)

    def load_comp(self, code, description, left_node, right_node):  # Добавление компетенции и места в списке
        params = {'token': ApeksAPI.TOKEN}
        data = {'table': 'plan_competencies',
                'fields[education_plan_id]': self.education_plan_id,
                'fields[code]': code,
                'fields[description]': description,
                'fields[level]': '1',
                'fields[left_node]': str(left_node),
                'fields[right_node]': str(right_node)}
        load = requests.post(ApeksAPI.URL + '/api/call/system-database/add', params=params, data=data)
        if load.json()['status'] == 0:
            return f"{code} {description} {load.json()['message']}"
        self.competencies = self.get_comp()

    def del_comp(self):  # Удаляет все компетенции из плана (если нельзя (связаны), то сообщение)
        message = []
        for i in range(len(self.competencies)):
            params = {'token': ApeksAPI.TOKEN,
                      'table': 'plan_competencies',
                      'filter[id]': self.competencies[i]['id']}
            remove = requests.delete(ApeksAPI.URL + '/api/call/system-database/delete', params=params)
            if remove.json()['status'] == 0:
                message.append(f"{self.competencies[i]['code']} {remove.json()['message']}")
        self.competencies = self.get_comp()
        return message

    def disciplines_comp(self):  # Получение связей дисциплин и компетенций
        message = []
        for disc in self.disciplines.keys():
            params = {'token': ApeksAPI.TOKEN,
                      'table': 'plan_curriculum_discipline_competencies',
                      'filter[curriculum_discipline_id]': disc}
            resp = requests.get(ApeksAPI.URL + '/api/call/system-database/get', params=params)
            if resp.json()['data']:
                message += resp.json()['data']
        return message

    def disciplines_all_comp_del(self):  # Удаление всех связей дисциплин, компетенций и их содержания в РП
        for curriculum_discipline_id in self.disciplines.keys():
            work_program_list = db_filter_req('mm_work_programs', 'curriculum_discipline_id', curriculum_discipline_id)
            for wp in work_program_list:
                if wp.get('id'):
                    disciplines_wp_clean(wp.get('id'))
            disciplines_comp_del(curriculum_discipline_id)


class CompMatrix:
    def __init__(self, filename):

        self.df = pd.read_excel(filename, engine='openpyxl', header=None).transpose().drop([0])
        # Normalize DataFrame
        replace_dict = {'  ': ' ', '–': '-', '. - ': ' - ', 'K': 'К', 'O': 'О',
                        '. з.': '.з.', '. у.': '.у.', '. в.': '.в.',
                        '.з .': '.з.', '.у .': '.у.', '.в .': '.в.'}
        for key, value in replace_dict.items():
            self.df[self.df.columns[0]] = self.df[self.df.columns[0]].str.replace(key, value, regex=False)

        self.disc_list = list(self.df.loc[1])

    def df_errors(self):  # Проверка матрицы на ошибки (распознавание индикаторов знать, уметь, владеть)
        not_found = []
        extensions_to_check = ['.з.', '.у.', '.в.']
        for k in range(len(self.df)):
            if all(ext not in matrix.df.at[k + 1, matrix.df.columns[0]] for ext in extensions_to_check):
                not_found.append(matrix.df.at[k + 1, matrix.df.columns[0]])
        return not_found

    def disc_check(self, discipline_name):  # Проверяем есть ли дисциплина в загруженной матрице (Google Sheets)
        return True if discipline_name in self.disc_list else False

    def disc_comp(self, discipline_name):  # Индикаторы и компетенции по дисциплине Матрице
        comp, complist = '', {}
        for i in range(len(self.df.loc[1]) - 1):
            if discipline_name == self.df.loc[1][i + 1]:
                for k in range(len(self.df)):
                    if self.df.at[k + 1, self.df.columns[i + 1]] == '+':
                        # Получаем компетенцию
                        if comp != self.df.at[k + 1, self.df.columns[0]].split('.')[0]:
                            comp = self.df.at[k + 1, self.df.columns[0]].split('.')[0]
                            complist[comp] = {'knowledge': [], 'abilities': [], 'ownerships': []}
                        # Получаем индикатор
                        data = self.df.at[k + 1, self.df.columns[0]]
                        load_data = f"- {data.split(' - ')[1]} ({data.split(' - ')[0]})"
                        if self.df.at[k + 1, self.df.columns[i + 1]] == "+" and '.з.' in str(data):
                            complist[comp]['knowledge'] += [load_data.replace('  ', ' ').replace('. (', ' (')]
                        elif self.df.at[k + 1, self.df.columns[i + 1]] == "+" and '.у.' in str(data):
                            complist[comp]['abilities'] += [load_data.replace('  ', ' ').replace('. (', ' (')]
                        elif self.df.at[k + 1, self.df.columns[i + 1]] == "+" and '.в.' in str(data):
                            complist[comp]['ownerships'] += [load_data.replace('  ', ' ').replace('. (', ' (')]
        return complist


class WorkProgram:
    def __init__(self, curriculum_discipline_id):
        self.curriculum_discipline_id = curriculum_discipline_id
        self.wp_data = db_filter_req('mm_work_programs', 'curriculum_discipline_id', curriculum_discipline_id)
        if not self.wp_data:
            self.create_wp()
            self.wp_data = db_filter_req('mm_work_programs', 'curriculum_discipline_id', curriculum_discipline_id)
        self.control_data = db_filter_req('plan_control_works', 'curriculum_discipline_id', curriculum_discipline_id)
        self.comp_level = db_filter_req('mm_competency_levels', 'work_program_id', self.wp_data[0]['id'])
        if not self.comp_level:
            self.comp_level_add()
            self.comp_level = db_filter_req('mm_competency_levels', 'work_program_id', self.wp_data[0]['id'])
        self.comp_data = self.comp_data_get()

    def get_main_staff_id(self):  # Получение идентификатора начальника кафедры или самого старшего на момент запроса
        department_id = db_filter_req('plan_curriculum_disciplines', 'id', self.curriculum_discipline_id)[0][
            'department_id']
        state_staff_id = db_filter_req('state_staff_history', 'department_id', department_id)[0]['staff_id']
        user_id = db_filter_req('state_staff', 'id', state_staff_id)[0]['user_id']
        return user_id

    def get_name(self):  # Название программы как у дисциплины плана
        disc_id = db_filter_req('plan_curriculum_disciplines', 'id', self.curriculum_discipline_id)[0]['discipline_id']
        return db_filter_req('plan_disciplines', 'id', disc_id)[0]['name']

    def create_wp(self):  # Cоздание программы
        params = {'token': ApeksAPI.TOKEN}
        data = {'table': 'mm_work_programs',
                'fields[curriculum_discipline_id]': self.curriculum_discipline_id,
                'fields[name]': self.get_name(),
                'fields[user_id]': self.get_main_staff_id()}
        requests.post(ApeksAPI.URL + '/api/call/system-database/add', params=params, data=data)

    def comp_level_add(self):  # Создание уровня сформированности компетенций (последний семестр [-1])
        if self.control_data:
            params = {'token': ApeksAPI.TOKEN}
            data = {'table': 'mm_competency_levels',
                    'fields[work_program_id]': self.wp_data[0]['id'],
                    'fields[semester_id]': self.control_data[-1]['semester_id'],
                    'fields[control_type_id]': self.control_data[-1]['control_type_id'],
                    'fields[level]': '1'}
            requests.post(ApeksAPI.URL + '/api/call/system-database/add', params=params, data=data)
            return "Уровень создан"
        else:
            return "Не заполнен план"

    def comp_level_edit(self, knowledge, abilities,
                        ownerships):  # Редактирование индикаторов в таблице Уровни сформированности
        if len(self.comp_level) > 1:  # Удаляем уровни если больше 1
            for i in self.comp_level:
                if i['level'] != '1':
                    params = {'token': ApeksAPI.TOKEN,
                              'table': 'mm_competency_levels',
                              'filter[work_program_id]': self.wp_data[0]['id'],
                              'filter[level]': i['level']}
                    requests.delete(ApeksAPI.URL + '/api/call/system-database/delete', params=params)

        if self.control_data:  # Проверка заполненности плана т.к. нужен семестр
            params = {'token': ApeksAPI.TOKEN}
            data = {'table': 'mm_competency_levels',
                    'filter[work_program_id]': self.wp_data[0]['id'],
                    'filter[level]': '1',
                    'fields[knowledge]': knowledge,
                    'fields[abilities]': abilities,
                    'fields[ownerships]': ownerships}
            requests.post(ApeksAPI.URL + '/api/call/system-database/edit', params=params, data=data)

    def comp_data_get(self):  # Получение данных о заполненных данных компетенций
        return db_filter_req('mm_work_programs_competencies_data', 'work_program_id', self.wp_data[0]['id'])

    def comp_data_add(self, competency_id, field_id, value):  # field_id 1-знать, 2-уметь, 3-владеть
        params = {'token': ApeksAPI.TOKEN}
        data = {'table': 'mm_work_programs_competencies_data',
                'fields[work_program_id]': self.wp_data[0]['id'],
                'fields[competency_id]': competency_id,
                'fields[field_id]': field_id,
                'fields[value]': value}
        requests.post(ApeksAPI.URL + '/api/call/system-database/add', params=params, data=data)
        self.comp_data = self.comp_data_get()

    #     def comp_data_edit(self, competency_id, field_id, value): # Редактирование заполненных данных
    #         data = {'token': ApeksAPI.TOKEN,
    #                 'table': 'mm_work_programs_competencies_data',
    #                 'filter[work_program_id]': self.wp_data[0]['id'],
    #                 'filter[competency_id]': competency_id,
    #                 'filter[field_id]': field_id,
    #                 'fields[value]': value,}
    #         requests.post(ApeksAPI.URL + '/api/call/system-database/edit', data=data)
    #         self.comp_data = self.comp_data_get()

    def comp_data_del(self):  # Удаление содержания компетенций
        params = {'token': ApeksAPI.TOKEN,
                  'table': 'mm_work_programs_competencies_data',
                  'filter[work_program_id]': self.wp_data[0]['id']}
        requests.delete(ApeksAPI.URL + '/api/call/system-database/delete', params=params)
        self.comp_data = self.comp_data_get()
