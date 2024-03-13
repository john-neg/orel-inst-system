from dataclasses import dataclass
import datetime
import logging
from typing import Any

from bson import ObjectId
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult

from config import MongoDBSettings
from .base_mongo_db_crud_service import BaseMongoDbCrudService, DocumentStatusType, VariousStaffDaytimeType
from ..db.mongo_db import get_mongo_db
from ..repository.mongo_db_repository import MongoDbRepository


@dataclass
class StaffVariousGroupDocStructure:
    """
    Класс структуры данных о группах переменного состава.

    Attributes
    ----------
    id: str
        id группы в Апекс-ВУЗ
    name: str
        Название группы
    type: str
        Тип подразделения
    daytime: str
        Время суток
    faculty: str
        Название факультета
    course: str
        Номер курса
    total: int
        Общее количество людей
    absence: dict
        Информация об отсутствии
    absence_illness: dict
        Информация об отсутствии по болезни
    user: str
        Имя пользователя системы
    updated: str
        Дата обновления
    """

    id: str
    name: str
    type: str
    daytime: VariousStaffDaytimeType
    faculty: str
    course: str
    total: int
    absence: dict
    absence_illness: dict
    user: str
    updated: str


@dataclass
class StaffVariousDocStructure:
    """Класс структуры данных строевой записки переменного состава."""

    date: datetime.date
    daytime: VariousStaffDaytimeType
    groups: dict[str, Any]
    status: DocumentStatusType

    def __dict__(self):
        return dict(
            date=self.date.isoformat(),
            daytime=self.daytime,
            groups=self.groups,
            status=self.status,
        )


@dataclass
class StaffVariousCRUDService(BaseMongoDbCrudService):
    """Класс для CRUD операций модели StaffVarious."""

    def change_status(
        self, _id: str | ObjectId, status: DocumentStatusType
    ) -> UpdateResult:
        """Меняет статус документа."""
        if isinstance(_id, str):
            _id = ObjectId(_id)
        return self.update(
            {"_id": _id},
            {"$set": {f"status": status}},
        )

    def make_blank_document(self, document_date: datetime.date, daytime: VariousStaffDaytimeType) -> InsertOneResult:
        """Создает пустой документ с заданной датой."""
        document = StaffVariousDocStructure(
            date=document_date,
            daytime=daytime.value,
            groups=dict(),
            status=DocumentStatusType.IN_PROGRESS,
        )
        result_info = self.create(document.__dict__())
        logging.info(
            f"Создан документ - строевая записка переменного состава "
            f"за {document_date.isoformat()}. {result_info}"
        )
        return result_info


def get_staff_various_document_service(
    mongo_db: Database = get_mongo_db(),
    collection_name: str = MongoDBSettings.STAFF_VARIOUS_COLLECTION,
) -> StaffVariousCRUDService:
    return StaffVariousCRUDService(
        repository=MongoDbRepository(mongo_db, collection_name)
    )
