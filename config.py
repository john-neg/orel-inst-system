import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import pytz
from dotenv import load_dotenv

load_dotenv()
BASEDIR = os.path.abspath(os.path.dirname(__file__))


class FlaskConfig(object):
    """Конфигурация Flask."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(BASEDIR, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMP_FILE_DIR = os.path.join(BASEDIR, "temp/")
    EXPORT_FILE_DIR = os.path.join(BASEDIR, "temp/export/")
    UPLOAD_FILE_DIR = os.path.join(BASEDIR, "temp/upload/")
    LOG_FILE_DIR = os.path.join(BASEDIR, "logs/")
    TEMPLATE_FILE_DIR = os.path.join(BASEDIR, "app/common/reports/templates/")
    STATIC_FILE_DIR = os.path.join(BASEDIR, "app/static/")
    ALLOWED_EXTENSIONS = {"xlsx", "csv"}

    # Группы пользователей
    ROLE_ADMIN: int = 1
    ROLE_USER: int = 2
    ROLE_METOD: int = 3
    ROLE_BIBL: int = 4


class ApeksConfig(object):
    """Конфигурация для работы с API АпексВУЗ"""

    # Данные API АпексВУЗ
    URL = os.getenv("APEKS_URL")
    TOKEN = os.getenv("APEKS_TOKEN")

    # ID типа подразделения "кафедра" в БД
    DEPT_ID = 4

    # Таблицы базы данных, используемые в приложении
    TABLES = {
        "load_groups": "load_groups",
        "load_subgroups": "load_subgroups",
        "mm_competency_levels": "mm_competency_levels",
        "mm_sections": "mm_sections",
        "mm_work_programs": "mm_work_programs",
        "mm_work_programs_data": "mm_work_programs_data",
        "mm_work_programs_signs": "mm_work_programs_signs",
        "mm_work_programs_competencies_data": "mm_work_programs_competencies_data",
        "mm_work_programs_competencies_fields": "mm_work_programs_competencies_fields",
        "plan_competencies": "plan_competencies",
        "plan_control_works": "plan_control_works",
        "plan_curriculum_disciplines": "plan_curriculum_disciplines",
        "plan_curriculum_discipline_competencies": "plan_curriculum_discipline_competencies",
        "plan_disciplines": "plan_disciplines",
        "plan_education_plans": "plan_education_plans",
        "plan_education_plans_education_forms": "plan_education_plans_education_forms",
        "plan_education_levels": "plan_education_levels",
        "plan_education_specialties": "plan_education_specialties",
        "plan_education_groups": "plan_education_groups",
        "plan_education_specializations": "plan_education_specializations",
        "plan_education_specializations_narrow": "plan_education_specializations_narrow",
        "plan_education_forms": "plan_education_forms",
        "plan_qualifications": "plan_qualifications",
        "plan_semesters": "plan_semesters",
        "schedule_day_schedule_lessons": "schedule_day_schedule_lessons",
        "schedule_day_schedule_lessons_staff": "schedule_day_schedule_lessons_staff",
        "state_departments": "state_departments",
        "state_special_ranks": "state_special_ranks",
        "state_staff": "state_staff",
        "state_staff_history": "state_staff_history",
        "state_staff_positions": "state_staff_positions",
        "system_settings": "system_settings",
        "system_users": "system_users",
    }

    MONTH_DICT = {
        1: "январь",
        2: "февраль",
        3: "март",
        4: "апрель",
        5: "май",
        6: "июнь",
        7: "июль",
        8: "август",
        9: "сентябрь",
        10: "октябрь",
        11: "ноябрь",
        12: "декабрь",
    }

    # Код уровня изучаемой дисциплины в таблице 'plan_disciplines'
    DISC_LEVEL = 3

    # Код типа 'группа дисциплин' в таблице 'plan_disciplines'
    DISC_TYPE = 16

    # ID полей БД АпексВУЗ в соответствующих таблицах
    MM_WORK_PROGRAMS = {
        # Название программы
        "name": "name",
        # Рецензенты
        "reviewers_ext": "reviewers_ext",
        # Дата создания
        "date_create": "date_create",
        # Дата протокола заседания кафедры
        "date_department": "date_department",
        # Номер протокола заседания кафедры
        "document_department": "document_department",
        # Дата протокола заседания метод. совета
        "date_methodical": "date_methodical",
        # Номер протокола заседания метод. совета
        "document_methodical": "document_methodical",
        # Дата протокола заседания ученого совета
        "date_academic": "date_academic",
        # Номер протокола заседания ученого совета
        "document_academic": "document_academic",
        # Дата утверждения
        "date_approval": "date_approval",
        # Статус утверждения
        "status": "status",
    }
    MM_SECTIONS = {
        # Цели дисциплины
        "purposes": "purposes",
        # Задачи дисциплины
        "tasks": "tasks",
        # Место в структуре ООП
        "place_in_structure": "place_in_structure",
        # Знать
        "knowledge": "knowledge",
        # Уметь
        "skills": "skills",
        # Владеть
        "abilities": "abilities",
        # Навыки
        "ownerships": "ownerships",
    }
    MM_WORK_PROGRAMS_DATA = {
        # Автор(ы) рабочей программы (для печати)
        "authorprint": 29,
        # Пояснение к таблице с последующими дисциплинами (информация об отсутствии)
        "no_next_disc": 30,
        # Примечание к тематическому плану
        "templan_info": 31,
        # Обеспечение самостоятельной работы
        "self_provision": 8,
        # Критерии оценки для сдачи промежуточной аттестации в форме тестирования
        "test_criteria": 32,
        # Тематика курсовых работ
        "course_works": 12,
        # Практикум
        "practice": 10,
        # Тематика контрольных работ
        "control_works": 13,
        # Примерные оценочные средства для проведения промежуточной аттестации
        "exam_form_desc": 33,
        # Задачи
        "task_works": 9,
        # Тесты
        "tests": 19,
        # Нормативные акты
        "regulations": 16,
        # Основная литература
        "library_main": 1,
        # Дополнительная литература
        "library_add": 2,
        # Научная продукция
        "library_np": 3,
        # Ресурсы информационно-телекоммуникационной сети Интернет
        "internet": 18,
        # Программное обеспечение
        "software": 15,
        # Базы данных, информационно-справочные и поисковые системы
        "ref_system": 17,
        # Описание материально-технической базы
        "materials_base": 20,
    }
    MM_WORK_PROGRAMS_SIGNS = {
        # ID пользователя
        "user_id": "user_id",
        # Время в формате "ГГГГ-ММ-ДД ЧЧ:ММ:СС"
        "timestamp": "timestamp",
    }
    MM_WORK_PROGRAMS_COMPETENCIES_DATA = {
        # Знать
        "knowledge": 1,
        # Уметь
        "abilities": 2,
        # Владеть
        "ownerships": 3,
    }
    MM_COMPETENCY_LEVELS = {
        # Номер уровня сформированности
        "level": "level",
        # ID семестра
        "semester_id": "semester_id",
        # ID формы контроля
        "control_type_id": "control_type_id",
        # Знать уровня сформированности
        "knowledge": "knowledge",
        # Уметь уровня сформированности
        "abilities": "abilities",
        # Владеть уровня сформированности
        "ownerships": "ownerships",
        # Уровень 1
        "level1": "level1",
        # Уровень 2
        "level2": "level2",
        # Уровень 3
        "level3": "level3",
    }

    # Базовый номер уровня сформированности
    BASE_COMP_LEVEL = 1

    # Регулярные выражения для выделения кодов индикаторов и компетенций
    COMP_FROM_IND_REGEX = r"\.[а-я]\."

    # RegExp для о
    FULL_CODE_SPLIT_REGEX = r"\s[-–]\s"

    # Виды индикаторов дисциплин
    INDICATOR_CODES = {
        ".з.": "knowledge",
        ".у.": "abilities",
        ".в.": "ownerships",
    }
    INDICATOR_TYPES = {
        "knowledge": "Знать",
        "abilities": "Уметь",
        "ownerships": "Владеть",
    }

    # Индекс строки расположения компетенций в загружаемых файлах матриц
    MATRIX_COMP_ROW = 0

    # Индекс колонки расположения дисциплин в загружаемых файлах матриц
    MATRIX_DISC_COL = 1

    # Идентификаторы видов занятий в таблице 'class_type_id'
    CLASS_TYPE_ID = {
        # Лекция
        "lecture": 1,
        # Семинар
        "seminar": 2,
        # Практическое занятие
        "prakt": 3,
    }

    # Идентификаторы форм контроля в таблице 'control_type_id'
    CONTROL_TYPE_ID = {
        # Экзамен
        "exam": 1,
        # Зачет
        "zachet": 2,
        # Зачет с оценкой
        "zachet_mark": 6,
        # Итоговая письменная аудиторная к/р
        "itog_kontr": 10,
        # Входной контроль
        "in_control": 12,
        # Выходной контроль
        "out_control": 13,
        # Итоговая аттестация
        "final_att": 14,
        # Консультация
        "group_cons": 15,
        # Кандидатский экзамен
        "kandidat_exam": 16,
    }

    # Статусы плана
    PLAN_STATUS = {0: "Не утвержден", 1: "Утвержден", 2: "Просрочен"}

    # Идентификаторы форм обучения в таблице 'education_form_id'
    EDUCATION_FORM_ID = {
        # Очное обучение
        "ochno": 1,
        # Заочное обучение
        "zaochno": 3,
        # Дополнительное проф образование
        "dpo": 5,
        # Проф. подготовка
        "prof_pod": 7,
    }

    # Идентификаторы уровней обучения в таблице 'education_level_id'
    EDUCATION_LEVEL_ID = {
        # Среднее профессиональное образование
        "spo": 2,
        # Бакалавриат
        "bak": 3,
        # Специалитет
        "spec": 5,
        # Адъюнктура
        "adj": 7,
    }

    # Список должностей кафедр не относящихся к ППС (не рассчитывается нагрузка)
    EXCLUDE_LIST = {
        12: "инструктора произв. обучения",
        13: "начальник кабинета",
        14: "специалист по УМР",
        15: "зав. кабинетом",
    }

    # Название разновидностей обеспечивающих материалов в рабочих программах
    # и входящие в каждую группу элементы.
    LIB_TYPES = {
        "library": [
            MM_WORK_PROGRAMS_DATA.get("library_main"),
            MM_WORK_PROGRAMS_DATA.get("library_add"),
        ],
        "library_np": [MM_WORK_PROGRAMS_DATA.get("library_np")],
        "library_int": [MM_WORK_PROGRAMS_DATA.get("internet")],
        "library_db": [MM_WORK_PROGRAMS_DATA.get("ref_system")],
    }

    # Коэффициенты для расчета нагрузки по формам контроля
    # на обучающегося и максимальное значение
    # Адъюнктура (итоговая аттестация, кандидатский экзамен)
    ADJ_KF: float = 1
    ADJ_KF_MAX: float = 8
    # Зачет
    ZACH_KF: float = 0.25
    ZACH_KF_MAX: float = 6
    # Экзамен
    EXAM_KF: float = 0.3
    EXAM_KF_MAX: float = 8
    # Итоговая аттестация (ПП, ДПО)
    FINAL_KF: float = 0.5
    FINAL_KF_MAX: float = 8

    # Типы занятий в отчете о нагрузке
    LOAD_LESSON_TYPES = ("lecture", "seminar", "pract", "group_cons")
    LOAD_CONTROL_TYPES = ("zachet", "exam", "final_att")

    # Типы обучающихся в отчете о нагрузке
    LOAD_STUDENT_TYPES = ("och", "zo_high", "zo_mid", "adj", "prof_pod", "dpo")

    # Часовой пояс для правильного отображения времени занятий
    TIMEZONE = pytz.timezone("Europe/Moscow")

    # Словарь для коррекции данных в загружаемых файлах матрицы компетенций
    COMP_REPLACE_DICT = {
        "     ": " ",
        "    ": " ",
        "   ": " ",
        "  ": " ",
        "–": "-",
        ". - ": " - ",
        "K": "К",  # Eng to RUS
        "O": "О",
        "A": "А",
        "B": "В",
        "C": "С",
        "H": "Н",
        "y": "у",
        ". з.": ".з.",
        ". у.": ".у.",
        ". в.": ".в.",
        ".з .": ".з.",
        ".у .": ".у.",
        ".в .": ".в.",
        "None": "",
    }


# Создание директорий если отсутствуют
for local_directory in (
    FlaskConfig.TEMP_FILE_DIR,
    FlaskConfig.EXPORT_FILE_DIR,
    FlaskConfig.UPLOAD_FILE_DIR,
    FlaskConfig.LOG_FILE_DIR,
):
    if not os.path.exists(local_directory):
        os.mkdir(local_directory, 0o755)

# Очистка временных директорий
for temp_directory in (
    FlaskConfig.EXPORT_FILE_DIR,
    FlaskConfig.UPLOAD_FILE_DIR,
):
    for file in os.listdir(temp_directory):
        os.remove(os.path.join(temp_directory, file))


# Logger Configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - [%(levelname)s] - %(funcName)s - %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        RotatingFileHandler(
            FlaskConfig.LOG_FILE_DIR + "system.log", maxBytes=5000000, backupCount=5
        ),
    ],
)
