from dataclasses import dataclass

from pymongo.database import Database

from config import MongoDBSettings
from .base_mongo_db_crud_service import BaseMongoDbCrudService
from ..db.mongo_db import get_mongo_db
from ..repository.mongo_db_repository import MongoDbRepository


@dataclass
class StaffLogsCRUDService(BaseMongoDbCrudService):
    """Класс для CRUD операций записи логов."""


def get_staff_logs_crud_service(
    mongo_db: Database = get_mongo_db(),
    collection_name: str = MongoDBSettings.STAFF_LOGS_COLLECTION,
) -> StaffLogsCRUDService:
    """Возвращает сервис для записи логов в MongoDB."""

    return StaffLogsCRUDService(repository=MongoDbRepository(mongo_db, collection_name))
