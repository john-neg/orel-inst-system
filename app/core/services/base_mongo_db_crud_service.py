from dataclasses import dataclass
from functools import singledispatchmethod
from typing import Optional

from bson import ObjectId
from pymongo.cursor import Cursor
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from ..repository.mongo_db_repository import MongoDbRepository, DocumentType


@dataclass
class BaseMongoDbCrudService:
    """Базовый класс CRUD операций для базы данных MongoDB."""

    repository: MongoDbRepository

    def list(self, *args, **kwargs) -> Cursor[DocumentType]:
        return self.repository.list(*args, **kwargs)

    def get(self, query_filter, *args, **kwargs) -> Optional[DocumentType]:
        return self.repository.get(query_filter, *args, **kwargs)

    @singledispatchmethod
    def get_by_id(self, _id: str, *args, **kwargs) -> Optional[DocumentType]:
        return self.repository.get({"_id": ObjectId(_id)}, *args, **kwargs)

    @get_by_id.register(ObjectId)
    def _(self, _id: ObjectId, *args, **kwargs):
        return self.repository.get({"_id": _id}, *args, **kwargs)

    def create(self, document, **kwargs) -> InsertOneResult:
        return self.repository.create(document, **kwargs)

    def update(self, query_filter, update, **kwargs) -> UpdateResult:
        return self.repository.update(query_filter, update, **kwargs)

    def delete(self, query_filter, *args, **kwargs) -> DeleteResult:
        return self.repository.delete(query_filter, *args, **kwargs)
