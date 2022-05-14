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
    EXPORT_FILE_DIR = os.path.join(BASEDIR, "app/files/export/")
    UPLOAD_FILE_DIR = os.path.join(BASEDIR, "app/files/upload/")
    LOG_FILE_DIR = os.path.join(BASEDIR, "logs/")
    TEMP_FILE_DIR = os.path.join(BASEDIR, "app/files/templates/")
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
        "plan_disciplines": "plan_disciplines",
        "plan_education_plans": "plan_education_plans",
        "plan_education_plans_education_forms": "plan_education_plans_education_forms",
        "schedule_day_schedule_lessons": "schedule_day_schedule_lessons",
        "schedule_day_schedule_lessons_staff": "schedule_day_schedule_lessons_staff",
        "state_departments": "state_departments",
        "state_staff": "state_staff",
        "state_staff_history": "state_staff_history",
        "state_staff_positions": "state_staff_positions",
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

    # ID полей БД АпексВУЗ в таблице 'mm_work_programs_data_items'
    MM_WORK_PROGRAMS_DATA_ITEMS = {
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
    LOAD_LESSON_TYPES = ["lecture", "seminar", "pract", "group_cons"]
    LOAD_CONTROL_TYPES = ["zachet", "exam", "final_att"]

    # Типы обучающихся в отчете о нагрузке
    LOAD_STUDENT_TYPES = ["och", "zo_high", "zo_mid", "adj", "prof_pod", "dpo"]

    # Часовой пояс для правильного отображения времени занятий
    TIMEZONE = pytz.timezone("Europe/Moscow")


# TODO убрать из конфига

# Create directories
for local_directory in (
    FlaskConfig.EXPORT_FILE_DIR,
    FlaskConfig.UPLOAD_FILE_DIR,
    FlaskConfig.LOG_FILE_DIR,
):
    if not os.path.exists(local_directory):
        os.mkdir(local_directory, 0o755)


# Logger Configuration
logging.basicConfig(
    level=logging.DEBUG,
    # encoding="utf-8",
    format="%(asctime)s, [%(levelname)s], %(funcName)s, %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        RotatingFileHandler(
            FlaskConfig.LOG_FILE_DIR + "system.log", maxBytes=5000000, backupCount=5
        ),
    ],
)
