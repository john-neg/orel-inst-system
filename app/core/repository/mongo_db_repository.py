from dataclasses import dataclass
from functools import singledispatchmethod
from typing import TypeVar, Optional, Mapping, Any

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult

from .abstract_repository import AbstractDBRepository

DocumentType = TypeVar("DocumentType", bound=Mapping[str, Any])


@dataclass
class MongoDbRepository(AbstractDBRepository):
    """Базовый класс операций с базой данных MongoDB."""

    mongo_db: Database
    collection_name: str

    def __post_init__(self):
        self.collection: Collection = self.mongo_db[self.collection_name]

    def list(self, *args, **kwargs) -> Cursor[DocumentType]:
        return self.collection.find(*args, **kwargs)

    def get(self, query_filter, *args, **kwargs) -> Optional[DocumentType] | None:
        return self.collection.find_one(query_filter, *args, **kwargs)

    @singledispatchmethod
    def get_by_id(self, _id: str, *args, **kwargs) -> Optional[DocumentType] | None:
        return self.get({"_id": ObjectId(_id)}, *args, **kwargs)

    @get_by_id.register(ObjectId)
    def _(self, _id: ObjectId, *args, **kwargs):
        return self.get({"_id": _id}, *args, **kwargs)

    def create(self, document: DocumentType, **kwargs) -> InsertOneResult:
        return self.collection.insert_one(document, **kwargs)

    def update(self, query_filter, update, **kwargs) -> UpdateResult:
        return self.collection.update_one(query_filter, update, **kwargs)

    def delete(self, query_filter, *args, **kwargs) -> DeleteResult:
        return self.collection.delete_one(query_filter, *args, **kwargs)
