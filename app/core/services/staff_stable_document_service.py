import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from bson import ObjectId
from pymongo.database import Database
from pymongo.results import UpdateResult, InsertOneResult

from config import MongoDBSettings, FlaskConfig
from .base_mongo_db_crud_service import BaseMongoDbCrudService
from ..db.mongo_db import get_mongo_db
from ..repository.mongo_db_repository import MongoDbRepository


class DocumentStatusType(str, Enum):
    """Класс статусов документа."""

    IN_PROGRESS = FlaskConfig.STAFF_IN_PROGRESS_STATUS
    COMPLETED = FlaskConfig.STAFF_COMPLETED_STATUS


@dataclass
class StaffStableDocStructure:
    """Класс структуры данных строевой записки постоянного состава."""

    date: datetime.date
    departments: dict[str, Any]
    status: DocumentStatusType

    def __dict__(self):
        return dict(
            date=self.date.isoformat(),
            departments=self.departments,
            status=self.status.value,
        )


@dataclass
class StaffStableCRUDService(BaseMongoDbCrudService):
    """Класс для CRUD операций модели StaffStable"""

    def change_status(
        self, _id: str | ObjectId, status: DocumentStatusType
    ) -> UpdateResult:
        """Меняет статус документа."""
        if isinstance(_id, str):
            _id = ObjectId(_id)
        return self.update(
            {"_id": _id},
            {"$set": {"status": status}},
        )

    def make_blank_document(self, document_date: datetime.date) -> InsertOneResult:
        """Создает пустой документ с заданной датой."""
        document = StaffStableDocStructure(
            date=document_date,
            departments=dict(),
            status=DocumentStatusType.IN_PROGRESS,
        )
        result_info = self.create(document.__dict__())
        logging.info(
            f"Создан документ - строевая записка постоянного состава "
            f"за {document_date.isoformat()}. {result_info}"
        )
        return result_info


def get_staff_stable_crud_service(
    mongo_db: Database = get_mongo_db(),
    collection_name: str = MongoDBSettings.STAFF_STABLE_COLLECTION,
) -> StaffStableCRUDService:
    return StaffStableCRUDService(
        repository=MongoDbRepository(mongo_db, collection_name)
    )
