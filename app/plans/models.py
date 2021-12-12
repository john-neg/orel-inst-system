import pandas as pd
import requests
from numpy import matrix
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from app.main.func import db_filter_req, db_request
from app.main.models import EducationPlan, ExcelStyle
from app.plans.func import disciplines_wp_clean
from config import ApeksAPI, FlaskConfig


class CompPlan(EducationPlan):
    def __init__(self, education_plan_id):
        super().__init__(education_plan_id)
        self.competencies = self.get_comp()

    def get_comp(self):
        """Получение списка компетенций плана"""
        return db_filter_req('plan_competencies', 'education_plan_id', self.education_plan_id)

    def get_comp_code_by_id(self, comp_id):
        """Получение кода компетенции по id"""
        for comp in self.competencies:
            if comp['id'] == comp_id:
                return comp["code"]

    def get_comp_by_id(self, comp_id):
        """Получение кода компетенции по id"""
        for comp in self.competencies:
            if comp['id'] == comp_id:
                return f'{comp["code"]} - {comp["description"]}'

    def load_comp(self, code, description, left_node, right_node):
        """Добавление компетенции и места в списке"""
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

    def del_comp(self):
        """Удаляет все компетенции из плана (если нельзя (связаны), то сообщение)"""
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

    def disciplines_comp(self):
        """Получение связей дисциплин и компетенций"""
        message = []
        for disc in self.disciplines.keys():
            params = {'token': ApeksAPI.TOKEN,
                      'table': 'plan_curriculum_discipline_competencies',
                      'filter[curriculum_discipline_id]': disc}
            resp = requests.get(ApeksAPI.URL + '/api/call/system-database/get', params=params)
            if resp.json()['data']:
                message += resp.json()['data']
        return message

    def disciplines_comp_dict(self):
        """Получение связей дисциплин и компетенций c названиями"""
        data = self.disciplines_comp()
        mtrx_dict = {}
        dics_id = 0
        if data:
            for i in data:
                if dics_id == i['curriculum_discipline_id']:
                    mtrx_dict[self.discipline_name(i['curriculum_discipline_id'])].append(
                        self.get_comp_by_id(i['competency_id']))
                else:
                    mtrx_dict[self.discipline_name(i['curriculum_discipline_id'])] = [
                        self.get_comp_by_id(i['competency_id'])]
                    dics_id = i['curriculum_discipline_id']
        return mtrx_dict

    def disciplines_all_comp_del(self):
        """Удаление компетенций, всех связей с дисциплинами и содержания из РП"""
        for curriculum_discipline_id in self.disciplines.keys():
            work_program_list = db_filter_req('mm_work_programs', 'curriculum_discipline_id', curriculum_discipline_id)
            for wp in work_program_list:
                if wp.get('id'):
                    disciplines_wp_clean(wp.get('id'))
            self.del_comp()

    def matrix_generate(self):
        disc_list = db_request("plan_disciplines")
        plan_data = db_filter_req("plan_curriculum_disciplines", "education_plan_id", self.education_plan_id)
        relations = self.disciplines_comp()

        # Сортировка
        plan_disc = {}
        for disc in plan_data:
            plan_disc[int(disc["left_node"])] = {
                "id": disc["id"],
                "code": disc["code"],
                "discipline_id": disc["discipline_id"],
                "level": disc["level"],
            }
        plan_comp = {}
        for comp in self.competencies:
            plan_comp[int(comp["left_node"])] = {"id": comp["id"], "code": comp["code"]}

        def disc_name(discipline_id):
            for discipline in disc_list:
                if discipline.get("id") == discipline_id:
                    return discipline["name"]

        wb = Workbook()
        ws = wb.active
        ws.title = "Матрица компетенций"
        ws.cell(1, 1).value = "Код"
        ws.cell(1, 1).style = ExcelStyle.Header
        ws.column_dimensions[get_column_letter(1)].width = 14
        ws.cell(1, 2).value = "Название дисциплины"
        ws.cell(1, 2).style = ExcelStyle.Header
        ws.column_dimensions[get_column_letter(2)].width = 60

        row = 2
        for disc in sorted(plan_disc):
            ws.cell(row, 1).value = plan_disc[disc]["code"]
            ws.cell(row, 1).style = ExcelStyle.Base
            ws.cell(row, 2).value = disc_name(plan_disc[disc]["discipline_id"])
            ws.cell(row, 2).style = ExcelStyle.Base
            column = 3
            for comp in sorted(plan_comp):
                ws.cell(1, column).value = plan_comp[comp]["code"]
                ws.cell(1, column).style = ExcelStyle.Header
                ws.cell(1, column).alignment = Alignment(text_rotation=90)
                ws.column_dimensions[get_column_letter(column)].width = 4
                ws.cell(row, column).style = ExcelStyle.Base
                ws.cell(row, column).alignment = Alignment(
                    horizontal="center", vertical="center"
                )
                if plan_disc[disc]["level"] != "3":
                    ws.cell(row, 1).style = ExcelStyle.BaseBold
                    ws.cell(row, 1).fill = ExcelStyle.GreyFill
                    ws.cell(row, 2).style = ExcelStyle.BaseBold
                    ws.cell(row, 2).fill = ExcelStyle.GreyFill
                    ws.cell(row, column).style = ExcelStyle.BaseBold
                    ws.cell(row, column).fill = ExcelStyle.GreyFill
                for relation in relations:
                    if (
                        plan_disc[disc]["id"] == relation["curriculum_discipline_id"]
                        and plan_comp[comp]["id"] == relation["competency_id"]
                    ):
                        ws.cell(row, column).value = "+"
                column += 1
            row += 1

        filename = "Матрица - " + self.name + ".xlsx"
        wb.save(FlaskConfig.EXPORT_FILE_DIR + filename)
        return filename

    def matrix_delete(self):
        """Удаление связей дисциплин и компетенций и их содержания в РП"""
        for curriculum_discipline_id in self.disciplines.keys():
            work_program_list = db_filter_req('mm_work_programs', 'curriculum_discipline_id',
                                              curriculum_discipline_id)
            for wp in work_program_list:
                if wp.get('id'):
                    disciplines_wp_clean(wp.get('id'))
            params = {'token': ApeksAPI.TOKEN,
                      'table': 'plan_curriculum_discipline_competencies',
                      'filter[curriculum_discipline_id]': curriculum_discipline_id}
            requests.delete(ApeksAPI.URL + '/api/call/system-database/delete', params=params)

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

    def df_errors(self):
        """Проверка матрицы на ошибки (распознавание индикаторов знать, уметь, владеть)"""
        not_found = []
        extensions_to_check = ['.з.', '.у.', '.в.']
        for k in range(len(self.df)):
            if all(ext not in matrix.df.at[k + 1, matrix.df.columns[0]] for ext in extensions_to_check):
                not_found.append(matrix.df.at[k + 1, matrix.df.columns[0]])
        return not_found

    def disc_check(self, discipline_name):
        """Проверяем есть ли дисциплина в загруженной матрице (Google Sheets)"""
        return True if discipline_name in self.disc_list else False

    def disc_comp(self, discipline_name):
        """Индикаторы и компетенции по дисциплине Матрице"""
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

    def get_main_staff_id(self):
        """Получение идентификатора начальника кафедры или самого старшего на момент запроса"""
        department_id = db_filter_req('plan_curriculum_disciplines', 'id', self.curriculum_discipline_id)[0][
            'department_id']
        state_staff_id = db_filter_req('state_staff_history', 'department_id', department_id)[0]['staff_id']
        user_id = db_filter_req('state_staff', 'id', state_staff_id)[0]['user_id']
        return user_id

    def get_name(self):
        """Название программы как у дисциплины плана"""
        disc_id = db_filter_req('plan_curriculum_disciplines', 'id', self.curriculum_discipline_id)[0]['discipline_id']
        return db_filter_req('plan_disciplines', 'id', disc_id)[0]['name']

    def create_wp(self):
        """Cоздание программы"""
        params = {'token': ApeksAPI.TOKEN}
        data = {'table': 'mm_work_programs',
                'fields[curriculum_discipline_id]': self.curriculum_discipline_id,
                'fields[name]': self.get_name(),
                'fields[user_id]': self.get_main_staff_id()}
        requests.post(ApeksAPI.URL + '/api/call/system-database/add', params=params, data=data)

    def comp_level_add(self):
        """Создание уровня сформированности компетенций (последний семестр [-1])"""
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
                        ownerships):
        """Редактирование индикаторов в таблице Уровни сформированности"""
        if len(self.comp_level) > 1:  # Удаляем уровни если больше 1
            for i in self.comp_level:
                if i['level'] != '1':
                    params = {'token': ApeksAPI.TOKEN,
                              'table': 'mm_competency_levels',
                              'filter[work_program_id]': self.wp_data[0]['id'],
                              'filter[level]': i['level']}
                    requests.delete(ApeksAPI.URL + '/api/call/system-database/delete', params=params)

        if self.control_data:
            """Проверка заполненности плана т.к. нужен семестр"""
            params = {'token': ApeksAPI.TOKEN}
            data = {'table': 'mm_competency_levels',
                    'filter[work_program_id]': self.wp_data[0]['id'],
                    'filter[level]': '1',
                    'fields[knowledge]': knowledge,
                    'fields[abilities]': abilities,
                    'fields[ownerships]': ownerships}
            requests.post(ApeksAPI.URL + '/api/call/system-database/edit', params=params, data=data)

    def comp_data_get(self):
        """Получение данных о заполненных данных компетенций"""
        return db_filter_req('mm_work_programs_competencies_data', 'work_program_id', self.wp_data[0]['id'])

    def comp_data_add(self, competency_id, field_id, value):
        """Загрузка данных компетенции (field_id 1-знать, 2-уметь, 3-владеть)"""
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

    def comp_data_del(self):
        """Удаление содержания компетенций"""
        params = {'token': ApeksAPI.TOKEN,
                  'table': 'mm_work_programs_competencies_data',
                  'filter[work_program_id]': self.wp_data[0]['id']}
        requests.delete(ApeksAPI.URL + '/api/call/system-database/delete', params=params)
        self.comp_data = self.comp_data_get()
