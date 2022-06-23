import re
from dataclasses import dataclass

from openpyxl import load_workbook

from common.classes.EducationPlan import EducationPlanCompetencies
from common.func.app_core import xlsx_iter_rows
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

    def xlsx_file_to_list(self) -> list:
        """Преобразует xlsx файл в список"""
        wb = load_workbook(self.file)
        ws = wb.active
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
        """Множество компетенций файла матрицы."""
        file_comp = {
            re.split(Apeks.INDICATOR_SPLIT_REGEX, self.file_list[0][i])[0]
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

    def matrix_simple_match_data(self) -> dict:
        """
        Сопоставляет данные из плана и файла для загрузки связей
        дисциплин и компетенций.

        Returns
        -------
            dict
                {"discipline_name": {"id": disc_id, "code": disc_code,
                "left_node": left_node, "comps": {"comp_name": comp_id}}.
        """
        match_data = {
            val.get("name"): {
                "id": key,
                "code": val.get("code"),
                "left_node": val.get("left_node"),
            }
            for key, val in self.disciplines.items()
            if val.get("level") == str(Apeks.DISC_LEVEL)
            and val.get("type") != str(Apeks.DISC_TYPE)
        }
        for disc in match_data:
            if disc in self.file_dict:
                match_data[disc]["comps"] = {}
                for comp in self.file_dict[disc]:
                    if comp in self.plan_competencies:
                        match_data[disc]["comps"][comp] = self.plan_competencies[comp]
        return match_data
