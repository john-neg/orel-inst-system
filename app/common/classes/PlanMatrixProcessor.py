import re
from dataclasses import dataclass

from openpyxl import load_workbook

from common.classes.EducationPlan import EducationPlanCompetencies
from common.func.app_core import xlsx_iter_rows, xlsx_normalize
from config import ApeksConfig as Apeks


@dataclass
class PlanMatrixProcessor:
    """
    Класс для обработки файлов с матрицами компетенций и подготовки данных
    для загрузки в учебные планы и рабочие программы плана.

    Attributes:
    ----------
        plan:
            экземпляр класса EducationPlanCompetencies
        file: str
            полный путь к файлу со списком компетенций

    Methods:
    -------
        xlsx_file_to_list() -> list:
            Преобразует xlsx файл в список
        xlsx_file_to_dict() -> dict:
            Обрабатывает данные из xlsx файла, преобразуя их в словарь.
            {discipline_name: [comp_match_list]}



    """

    plan: EducationPlanCompetencies
    file: str

    def __post_init__(self) -> None:
        self.plan_competencies = {
            comp.get("code"): key for key, comp in self.plan.plan_competencies.items()
        }
        self.file_list = self.xlsx_file_to_list()
        self.file_dict = self.xlsx_file_to_dict()
        self.disciplines = self.plan.plan_curriculum_disciplines
        self.indicator_errors = set()

    def xlsx_file_to_list(self) -> list:
        """Преобразует xlsx файл в список"""
        wb = load_workbook(self.file)
        ws = xlsx_normalize(wb.active, Apeks.COMP_REPLACE_DICT)
        file_list = list(xlsx_iter_rows(ws))
        return file_list

    def xlsx_file_to_dict(self) -> dict:
        """
        Обрабатывает данные из xlsx файла, преобразуя их в словарь.

        Returns
        -------
            dict
                {discipline_name: [comp_match_list]}
        """
        file_dict = {}
        for line in self.file_list:
            disc_name = line[1]
            file_dict[disc_name] = []
            for i in range(2, len(line)):
                if line[i] == "+":
                    comp_code = self.file_list[0][i]
                    file_dict[disc_name].append(comp_code)
        return file_dict

    def matrix_file_comp(self) -> set:
        """Возвращает множество (set) компетенций файла матрицы."""
        file_comp = {
            re.split(Apeks.COMPETENCY_SPLIT_REGEX, self.file_list[0][i])[0]
            for i in range(2, len(self.file_list[0]))
        }
        return file_comp

    def comp_not_in_file(self) -> set:
        """Компетенции плана, отсутствующие в файле."""
        plan_comp = set(self.plan_competencies)
        file_comp = self.matrix_file_comp()
        return file_comp.difference(plan_comp)

    def comp_not_in_plan(self) -> set:
        """Компетенции файла, отсутствующие в плане."""
        plan_comp: set = set(self.plan_competencies)
        file_comp = self.matrix_file_comp()
        return plan_comp.difference(file_comp)

    def get_match_data_template(self) -> dict:
        """
        Возвращает шаблон словаря заполненный данными из плана, готовый для
        для заполнения связанными данными файла.

        Returns
        -------
            dict
                {"discipline_name": {"id": disc_id, "code": disc_code,
                "left_node": left_node}.
        """

        disciplines = sorted(
            self.disciplines.values(), key=lambda d: int(d['left_node'])
        )
        match_data = {
            val.get("name"): {
                "id": val.get("id"),
                "code": val.get("code"),
                "left_node": val.get("left_node"),
            }
            for val in disciplines
            if val.get("level") == str(Apeks.DISC_LEVEL)
            and val.get("type") != str(Apeks.DISC_TYPE)
        }
        return match_data

    def matrix_simple_match_data(self) -> dict:
        """
        Сопоставляет данные из плана и файла для загрузки связей
        дисциплин и компетенций из простой матрицы.

        Returns
        -------
            dict
                {"discipline_name": {"id": disc_id, "code": disc_code,
                "left_node": left_node, "comps": {"comp_name": comp_id}}.
        """
        match_data = self.get_match_data_template()
        for disc in match_data:
            if disc in self.file_dict:
                match_data[disc]["comps"] = {}
                for comp_code in self.file_dict[disc]:
                    if comp_code in self.plan_competencies:
                        match_data[disc]["comps"][comp_code] = self.plan_competencies[
                            comp_code
                        ]
        return match_data

    def matrix_indicator_match_data(self) -> dict:
        """
        Сопоставляет данные из плана и файла для загрузки связей
        дисциплин и компетенций из матрицы с индикаторами.

        Returns
        -------
            dict
                {"discipline_name": {"id": disc_id, "code": disc_code,
                "left_node": left_node, "comps": {"comp_name": {"id": comp_id,
                "knowledge": [val], "abilities": [val], "ownerships":[val]}}}}.
        """
        match_data = self.get_match_data_template()
        ind_regex = re.compile(Apeks.COMPETENCY_SPLIT_REGEX)
        for disc in match_data:
            disc_name = f"{match_data[disc].get('code')} {disc}"
            if disc_name in self.file_dict:
                match_data[disc]["comps"] = {}
                for ind in self.file_dict[disc_name]:
                    comp_code = re.split(Apeks.COMPETENCY_SPLIT_REGEX, ind, 1)[0]
                    try:
                        ind_code, ind_val = re.split(Apeks.INDICATOR_SPLIT_REGEX, ind, 1)
                        ind_separator = ind_regex.search(ind_code).group()
                    except AttributeError:
                        self.indicator_errors.add(ind)
                    else:
                        if ind_separator and comp_code in self.plan_competencies:
                            ind_type = Apeks.INDICATOR_TYPES.get(ind_separator)
                            comp_data = match_data[disc]["comps"].setdefault(
                                comp_code,
                                {
                                    "id": self.plan_competencies[comp_code],
                                    "knowledge": [],
                                    "abilities": [],
                                    "ownerships": [],
                                },
                            )
                            comp_data[ind_type].append(f"{ind_val} ({ind_code})")
                        else:
                            self.indicator_errors.add(ind)
        return match_data
