from functools import singledispatchmethod
from typing import Optional

from bson import ObjectId

from ..repository.mongo_db_repository import MongoDbRepository, DocumentType


class MongoCRUDService(MongoDbRepository):
    @singledispatchmethod
    def get_by_id(self, _id: str, *args, **kwargs) -> Optional[DocumentType] | None:
        return self.get({"_id": ObjectId(_id)}, *args, **kwargs)

    @get_by_id.register(ObjectId)
    def _(self, _id: ObjectId, *args, **kwargs):
        return self.get({"_id": _id}, *args, **kwargs)
