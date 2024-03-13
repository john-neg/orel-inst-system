import logging
import os
from datetime import timedelta

import pytz
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, ".env"))


class FlaskConfig(object):
    """Конфигурация Flask."""

    SECRET_KEY = os.getenv("SECRET_KEY", "DEFAULT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get(
            "DATABASE_URL", f"sqlite:///{os.path.join(BASEDIR, 'app.db')}"
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMP_FILE_DIR = os.path.join(BASEDIR, "temp/")
    EXPORT_FILE_DIR = os.path.join(BASEDIR, "temp/export/")
    UPLOAD_FILE_DIR = os.path.join(BASEDIR, "temp/upload/")
    LOG_FILE_DIR = os.path.join(BASEDIR, "logs/")
    TEMPLATE_FILE_DIR = os.path.join(BASEDIR, "app/core/reports/templates/")
    STATIC_FILE_DIR = os.path.join(BASEDIR, "app/static/")
    ALLOWED_EXTENSIONS = {"xlsx", "csv"}
    USER_LOGIN_DURATION = timedelta(hours=8)

    # Pagination
    ITEMS_PER_PAGE = 15
    AVAILABLE_PAGES = 3

    # LDAP Config
    LDAP_AUTH = os.getenv("LDAP_AUTH") in ('True', 'true', '1')
    AD_DOMAIN = os.getenv("AD_DOMAIN")
    AD_SERVER = os.getenv("AD_SERVER")
    AD_SEARCH_TREE = os.getenv("AD_SEARCH_TREE")

    ORGANIZATION_NAME: str = os.getenv("ORGANIZATION_NAME", "Образовательная организация")


class PermissionsConfig:
    """Настройки прав доступа."""

    # Базовые роли
    ROLE_ADMIN: str = "admin"
    ROLE_USER: str = "user"
    BASE_ROLES = {
        ROLE_ADMIN: "Администратор",
        ROLE_USER: "Пользователь",
    }

    # Разрешения
    LIBRARY_LOAD_INFO_SYSTEMS_PERMISSION: str = "library_load_info_systems"
    LIBRARY_LOAD_INTERNET_LINKS_PERMISSION: str = "library_load_internet_links"
    LIBRARY_LOAD_SCIENCE_PRODUCTS_PERMISSION: str = "library_load_science_products"
    LIBRARY_LOAD_SOURCES_PERMISSION: str = "library_load_sources"
    PAYMENTS_DATA_EDIT_PERMISSION: str = "payments_data_edit"
    PLAN_MATRIX_EDIT_PERMISSION: str = "plan_matrix_edit"
    PRODUCTION_CALENDAR_EDIT_PERMISSION: str = "production_calendar_edit"
    PROGRAMS_EDIT_FIELDS_PERMISSION: str = "programs_edit_fields"
    PROGRAMS_VIEW_PLAN_INFO_PERMISSION: str = "programs_view_plan_info"
    REPORT_HOLIDAYS_PERMISSION: str = "report_holidays"
    STAFF_BUSY_TYPES_EDIT_PERMISSION: str = "staff_busy_types_edit"
    STAFF_CLOSE_DOCUMENT_PERMISSION: str = "staff_close_document"
    STAFF_REPORT_PERMISSION: str = "staff_report"
    USERS_EDIT_PERMISSION: str = "users_edit"
    PERMISSION_DESCRIPTIONS = {
        LIBRARY_LOAD_INFO_SYSTEMS_PERMISSION: "Обеспечение - загрузка баз данных и инф.-справ. систем",
        LIBRARY_LOAD_INTERNET_LINKS_PERMISSION: "Обеспечение - загрузка интернет ресурсов в рабочие программы",
        LIBRARY_LOAD_SCIENCE_PRODUCTS_PERMISSION: "Обеспечение - загрузка научной продукции в рабочие программы",
        LIBRARY_LOAD_SOURCES_PERMISSION: "Обеспечение - загрузка списка литературы в рабочие программы",
        PAYMENTS_DATA_EDIT_PERMISSION: "Инструменты - редактирование данных расчета денежного содержания",
        PLAN_MATRIX_EDIT_PERMISSION: "Учебные планы - загрузка и удаление компетенций и индикаторов",
        PRODUCTION_CALENDAR_EDIT_PERMISSION: "Производственный календарь - редактирование",
        PROGRAMS_EDIT_FIELDS_PERMISSION: "Программы - создание и внесение изменений в РП",
        PROGRAMS_VIEW_PLAN_INFO_PERMISSION: "Программы - доступ к информации на уровне уч. плана",
        REPORT_HOLIDAYS_PERMISSION: "Отчеты - занятость в выходные",
        STAFF_BUSY_TYPES_EDIT_PERMISSION: "Строевая записка - редактирование видов отвлечений",
        STAFF_CLOSE_DOCUMENT_PERMISSION: "Строевая записка - установка разрешения/запрета на редактирование документа",
        STAFF_REPORT_PERMISSION: "Строевая записка - просмотр отчетов",
        USERS_EDIT_PERMISSION: "Пользователи - права и редактирование",
    }


class MongoDBSettings:
    """Настройки для базы данных MongoDB."""

    # Имя пользователя БД
    MONGO_DB_USER = os.getenv('MONGO_DB_USER')
    # Пароль
    MONGO_DB_PASS = os.getenv('MONGO_DB_PASS')
    # Адрес сервера БД
    MONGO_DB_URL = os.getenv('MONGO_DB_URL')
    # Имя базы данных
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
    # Источник аутентификации
    MONGO_DB_AUTH_SOURCE = os.getenv('MONGO_DB_AUTH_SOURCE', 'admin')
    # Механизм аутентификации
    MONGO_DB_AUTH_MECHANISM = os.getenv('MONGO_DB_AUTH_MECHANISM', 'DEFAULT')
    # Строка подключения к БД
    CONNECTION_STRING = (
        f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASS}@{MONGO_DB_URL}"
        f"/?authMechanism={MONGO_DB_AUTH_MECHANISM}&authSource={MONGO_DB_AUTH_SOURCE}"
    )
    # Название коллекции данных переменного состава
    STAFF_STABLE_COLLECTION = 'stable_staff'
    # Название коллекции данных постоянного состава
    STAFF_VARIOUS_COLLECTION = 'various_staff'
    # Название коллекции истории операций
    STAFF_LOGS_COLLECTION = 'staff_logs'

    # Статусы документа для строевой записки
    # Название статуса документа "в процессе"
    STAFF_IN_PROGRESS_STATUS: str = 'in progress'
    # Название статуса завершенного документа
    STAFF_COMPLETED_STATUS: str = 'completed'
    # Название историй операций
    STAFF_COLLECTION_STATUSES = {
        STAFF_IN_PROGRESS_STATUS: "Редактируется",
        STAFF_COMPLETED_STATUS: "Сформирован"
    }

    # Время подачи строевой записки
    DAYTIME_MORNING = "morning"
    DAYTIME_DAY = "day"
    DAYTIME_EVENING = "evening"
    DAYTIME_NAME = {
        DAYTIME_MORNING: "Утро (8:30)",
        DAYTIME_DAY: "День (14:30)",
        DAYTIME_EVENING: "Вечер (21:30)",
    }


class LoggerConfig(object):
    """Logger Configuration."""

    LEVEL = logging.DEBUG
    FORMAT = "%(asctime)s - [%(levelname)s] - %(funcName)s - %(message)s"
    LOG_FILE = os.path.join(FlaskConfig.LOG_FILE_DIR, "system.log")
    MAX_BYTES = 5242880
    BACKUP_COUNT = 10


class ApeksConfig(object):
    """Конфигурация для работы с API АпексВУЗ"""

    # Данные для запросов по API к АпексВУЗ
    URL = os.getenv("APEKS_URL")
    TOKEN = os.getenv("APEKS_TOKEN")

    # Точки доступа к данным АпексВУЗ
    DB_GET_ENDPOINT = f"{URL}/api/call/system-database/get"
    DB_ADD_ENDPOINT = f"{URL}/api/call/system-database/add"
    DB_EDIT_ENDPOINT = f"{URL}/api/call/system-database/edit"
    DB_DEL_ENDPOINT = f"{URL}/api/call/system-database/delete"
    STUDENT_SCHEDULE_ENDPOINT = f"{URL}/api/call/schedule-schedule/student"
    STAFF_SCHEDULE_ENDPOINT = f"{URL}/api/call/schedule-schedule/staff"

    # Типы подразделений (для поля type таблицы "state_departments")
    TYPE_DEPARTM = "0"
    TYPE_KAFEDRA = "1"
    TYPE_FACULTY = "2"
    DEPT_TYPES = {
        TYPE_DEPARTM: "Подразделения",
        TYPE_KAFEDRA: "Кафедры",
        TYPE_FACULTY: "Факультеты",
    }

    # Таблицы базы данных Апекс-ВУЗ, используемые в приложении
    LOAD_GROUPS_TABLE = "load_groups"
    STATE_DEPARTMENTS_TABLE = "state_departments"
    STATE_STAFF_HISTORY_TABLE = "state_staff_history"
    STATE_STAFF_POSITIONS_TABLE = "state_staff_positions"
    STATE_STAFF_TABLE = "state_staff"
    STATE_VACANCIES_TABLE = "state_vacancies"
    STUDENT_STUDENTS_GROUPS_TABLE = "student_students_groups"
    STUDENT_STUDENTS_TABLE = "student_students"
    STUDENT_STUDENT_HISTORY_TABLE = "student_student_history"

    TABLES = {
        "load_groups": "load_groups",
        "load_subgroups": "load_subgroups",
        "mm_competency_levels": "mm_competency_levels",
        "mm_methodical_items": "mm_methodical_items",
        "mm_methodical_items_files": "mm_methodical_items_files",
        "mm_sections": "mm_sections",
        "mm_work_programs": "mm_work_programs",
        "mm_work_programs_competencies_data": "mm_work_programs_competencies_data",
        "mm_work_programs_competencies_fields": "mm_work_programs_competencies_fields",
        "mm_work_programs_data": "mm_work_programs_data",
        "mm_work_programs_signs": "mm_work_programs_signs",
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
        "state_vacancies": "state_vacancies",
        "system_files": "system_files",
        "system_reports": "system_reports",
        "system_settings": "system_settings",
        "system_users": "system_users",
    }

    # Типы записей в таблице student_student_history означающие исключение из группы
    STUDENT_HISTORY_RECORD_TYPES = {
        3: "Перевод в другую группу",
        5: "Академический отпуск",
        6: "Отчисление",
        10: "Отчисление в связи с выпуском",
        12: "Перевод на ускоренное обучение",
        14: "Перевод на другую образовательную программу"
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

    # Код типа дисциплины Концентрированная практика
    DISC_CONC_PRACT_TYPE = 1

    # Код типа дисциплины Распределенная практика
    DISC_RASP_PRACT_TYPE = 2

    # Код типа дисциплины ГИА
    DISC_GIA_TYPE = 4

    # Код типа дисциплины Группа дисциплин
    DISC_GROUP_TYPE = 16

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
        # Дата протокола заседания метод совета
        "date_methodical": "date_methodical",
        # Номер протокола заседания метод совета
        "document_methodical": "document_methodical",
        # Дата протокола заседания ученого совета
        "date_academic": "date_academic",
        # Номер протокола заседания ученого совета
        "document_academic": "document_academic",
        # Дата утверждения
        "date_approval": "date_approval",
        # Статус утверждения
        "status": "status",
        # Шаблон для печати по умолчанию
        "settings": "settings",
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

    SYSTEM_REPORTS = {
        # Шаблоны рабочих программ
        "work_program_template": 3030,
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

    # Статусы учебных планов
    PLAN_STATUS = {
        0: "Не утвержден",
        1: "Утвержден",
        2: "Просрочен",
    }

    # Поколения учебных планов
    PLAN_GENERATIONS = {
        "3": "ФГОС 3",
        "3+": "ФГОС 3+",
        "3++": "ФГОС 3++",
        "R": "ФГТ",
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
        "adj-fgt": 10,
    }

    # Идентификаторы должностей кафедр не относящихся к ППС (не рассчитывается нагрузка)
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
