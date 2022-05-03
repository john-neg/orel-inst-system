from app.main.func import db_filter_req, add_wp_field
from app.main.models import EducationPlan
from config import ApeksConfig as Apeks


class LibraryPlan(EducationPlan):
    def __init__(self, education_plan_id):
        super().__init__(education_plan_id)
        self.work_programs, self.non_exist = self.wp_data()

    def wp_data(self):
        work_programs, non_exist = {}, {}
        for disc in self.disciplines:
            response = db_filter_req(
                "mm_work_programs", "curriculum_discipline_id", disc
            )
            if response:
                wp_id = response[0]["id"]
                wp_name = response[0]["name"]
                work_programs[wp_id] = wp_name
            else:
                non_exist[disc] = " ".join(self.disciplines[str(disc)])
        return work_programs, non_exist

    def library_content(self):
        library_fields = [
            Apeks.MM_WORK_PROGRAMS_DATA_ITEMS.get('library_main'),
            Apeks.MM_WORK_PROGRAMS_DATA_ITEMS.get('library_add'),
            Apeks.MM_WORK_PROGRAMS_DATA_ITEMS.get('library_np'),
            Apeks.MM_WORK_PROGRAMS_DATA_ITEMS.get('internet'),
            Apeks.MM_WORK_PROGRAMS_DATA_ITEMS.get('ref_system'),
        ]

        def lib_data(field_id):
            for f in reversed(wp_fields):
                if f.get("field_id") == str(field_id):
                    return "" if f.get("data") is None else f.get("data")

        content = {}
        for disc in self.disciplines:
            wp_data = db_filter_req(
                "mm_work_programs", "curriculum_discipline_id", disc
            )
            if wp_data:
                wp_fields = db_filter_req(
                    "mm_work_programs_data", "work_program_id", wp_data[0]["id"]
                )
                if not wp_fields:
                    for field in library_fields:
                        add_wp_field(wp_data[0]["id"], field)

                field_dict = {}
                for field in library_fields:
                    field_dict[field] = lib_data(field)
                content[wp_data[-1]["name"]] = field_dict
                # [-1] - это костыль т.к. в бд бывает дублирование,
                # и тогда нужен именно последний объект

            else:
                field_dict = {}
                for field in library_fields:
                    field_dict[field] = "Нет программы"
                content[self.disciplines[disc][1]] = field_dict
        return content
