import sys

from pymongo.errors import CollectionInvalid

sys.path.append(".")

from app.core.db.mongo_db import get_mongo_db
from config import MongoDBSettings

db = get_mongo_db()

collections = [
    MongoDBSettings.STAFF_STABLE_COLLECTION,
    MongoDBSettings.STAFF_VARIOUS_COLLECTION,
    MongoDBSettings.STAFF_LOGS_COLLECTION
]

for collection in collections:
    try:
        db.create_collection(collection)
    except CollectionInvalid:
        pass
