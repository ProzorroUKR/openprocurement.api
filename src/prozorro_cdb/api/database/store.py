import os
from contextlib import asynccontextmanager
from contextvars import ContextVar, Token
from decimal import Decimal
from logging import getLogger
from typing import Any, Dict, List, Optional, Self, TypeVar
from uuid import uuid4

from bson.codec_options import CodecOptions, TypeCodec, TypeRegistry
from bson.decimal128 import Decimal128
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorClientSession,
    AsyncIOMotorCollection,
)
from pydantic import BaseModel
from pymongo import ASCENDING, DESCENDING, IndexModel, ReadPreference, ReturnDocument
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from prozorro_cdb.api.context import get_now_async

logger = getLogger("{}.init".format(__name__))


#  mongodb
class MongodbResourceConflict(Exception):
    """
    On doc update we pass _id and _rev as filter
    _rev can be changed by concurrent requests
    then update_one(or replace_one) doesn't find any document to update and returns matched_count = 0
    that causes MongodbResourceConflict that is shown to the User as 409 response code
    that means they have to retry his request
    """


class DecimalCodec(TypeCodec):
    python_type = Decimal  # the Python type acted upon by this type codec
    bson_type = Decimal128  # the BSON type acted upon by this type codec

    def transform_python(self, value):
        """Function that transforms a custom type value into a type
        that BSON can encode."""
        return Decimal128(value)

    def transform_bson(self, value):
        """Function that transforms a vanilla BSON type value into our
        custom type."""
        return value.to_decimal()


type_registry = TypeRegistry(
    [
        DecimalCodec(),
    ],
)
codec_options = CodecOptions(type_registry=type_registry)


def get_public_modified():
    public_modified = {"$divide": [{"$toLong": "$$NOW"}, 1000]}
    return public_modified


class MongodbStore:
    collections = {}
    instance = None

    @classmethod
    def create_instance(cls, settings) -> Self:
        if cls.instance is None:
            cls.instance = cls(settings)
        return cls.instance

    @classmethod
    def get_instance(cls) -> Self:
        if cls.instance is None:
            raise RuntimeError("DB is not initialized")
        return cls.instance

    @classmethod
    def drop_instance(cls) -> Self:
        cls.instance = None

    def __init__(self, settings):
        self.settings = settings

        db_name = os.environ.get("DB_NAME", settings["mongodb.db_name"])
        mongodb_uri = os.environ.get("MONGODB_URI", settings["mongodb.uri"])
        max_pool_size = int(os.environ.get("MONGODB_MAX_POOL_SIZE", settings["mongodb.max_pool_size"]))
        min_pool_size = int(os.environ.get("MONGODB_MIN_POOL_SIZE", settings["mongodb.min_pool_size"]))

        # https://docs.mongodb.com/manual/core/causal-consistency-read-write-concerns/#causal-consistency-and-read-and-write-concerns
        raw_read_preference = os.environ.get(
            "READ_PREFERENCE",
            settings.get("mongodb.read_preference", "SECONDARY_PREFERRED"),
        )
        raw_w_concert = os.environ.get("WRITE_CONCERN", settings.get("mongodb.write_concern", "majority"))
        raw_r_concern = os.environ.get("READ_CONCERN", settings.get("mongodb.read_concern", "majority"))
        self.connection = AsyncIOMotorClient(
            mongodb_uri,
            maxPoolSize=max_pool_size,
            minPoolSize=min_pool_size,
        )
        self.database = self.connection.get_database(
            db_name,
            read_preference=getattr(ReadPreference, raw_read_preference),
            write_concern=WriteConcern(w=int(raw_w_concert) if raw_w_concert.isnumeric() else raw_w_concert),
            read_concern=ReadConcern(level=raw_r_concern),
            codec_options=codec_options,
        )

        self.add_collection("sequences", SequencesCollection)

    def __getattr__(self, name):
        """
        Used in code related to specific packages, like:
        >>> store = MongodbStore(settings)
        >>> store.add_collection("tenders", TenderCollection)
        >>> store.add_collection("plans", PlanCollection)
        >>> store.plans.get(uid)
        >>> store.tenders.save(doc)
        >>> store.tenders.count(filters)

        :param name: collection name
        :return: collection instance
        """
        if name in self.collections:
            return self.collections[name]
        raise AttributeError(f"MongodbStore has no attribute {name}: {list(self.collections.keys())}")

    def add_collection(self, name, cls):
        self.collections[name] = cls(self, self.settings)

    async def create_indexes(self, *_):
        for collection in self.collections.values():
            await collection.create_indexes()

    @staticmethod
    def get_next_rev(current_rev=None):
        """
        This mimics couchdb _rev field
        that prevents concurrent updates
        :param current_rev:
        :return:
        """
        if current_rev:
            version, _ = current_rev.split("-")
            version = int(version)
        else:
            version = 1
        next_rev = f"{version + 1}-{uuid4().hex}"
        return next_rev

    @staticmethod
    async def get(collection, uid):
        res = await collection.find_one(
            {"_id": uid},
            projection={
                "is_public": False,
                "is_test": False,
            },
            session=get_db_session_async(),
        )
        return res

    async def list(
        self,
        collection,
        fields,
        inclusive_filter: bool = False,
        offset_field="_id",
        offset_value=None,
        mode="all",
        descending=False,
        limit=0,
        filters=None,
    ):
        filters = filters or {}
        filters["is_public"] = True
        if mode == "test":
            filters["is_test"] = True
        elif mode != "_all_":
            filters["is_test"] = False
        if offset_value:
            suffix = "e" if inclusive_filter else ""
            operator = "$lt" if descending else "$gt"
            filters[offset_field] = {operator + suffix: offset_value}
        results = await collection.find(
            filter=filters,
            projection={f: 1 for f in fields},
            limit=limit,
            sort=((offset_field, DESCENDING if descending else ASCENDING),),
            session=get_db_session_async(),
        ).to_list(None)
        for e in results:
            self.rename_id(e)
        return results

    async def save_data(self, collection, data, insert=False, modified=True):
        uid = data.pop("id" if "id" in data else "_id")
        revision = data.pop("rev" if "rev" in data else "_rev", None)

        data["_id"] = uid
        data["_rev"] = self.get_next_rev(revision)
        data["is_public"] = data.get("status") not in ("draft", "deleted")
        data["is_test"] = data.get("mode") == "test"
        if "is_masked" in data and data.get("is_masked") is not True:
            data.pop("is_masked")

        pipeline = [
            {"$replaceWith": {"$literal": data}},
        ]
        now = get_now_async()
        if insert:
            data["dateCreated"] = now.isoformat()  # TODO: THIS IS STATE CLASS RESPONSIBILITY
        if modified:
            data["dateModified"] = now.isoformat()  # TODO: THIS IS STATE CLASS RESPONSIBILITY
            pipeline.append(
                {
                    "$set": {
                        "public_modified": get_public_modified(),
                    }
                }
            )
        result = await collection.update_one(
            {"_id": uid, "_rev": revision},
            pipeline,
            upsert=insert,
            session=get_db_session_async(),
        )
        if not result.modified_count and not result.upserted_id:
            raise MongodbResourceConflict("Conflict while updating document. Please, retry")
        return data

    @staticmethod
    async def flush(collection):
        result = await collection.delete_many({})
        return result

    @staticmethod
    async def delete(collection, uid):
        result = await collection.delete_one({"_id": uid}, session=get_db_session_async())
        return result

    @staticmethod
    def rename_id(obj):
        if obj:
            obj["id"] = obj.pop("_id")
        return obj

    @staticmethod
    async def find(collection: AsyncIOMotorCollection, filters: Dict[str, Any]) -> List[Any]:
        result = await collection.find(filter=filters, session=get_db_session_async()).to_list(None)
        return result


SaveDataT = TypeVar("SaveDataT", bound=BaseModel)


class BaseCollection:
    store: MongodbStore
    object_name = "dummy"
    collection_name: Optional[str] = None  # collection name can be hardcoded

    def __init__(self, store, settings):
        self.store = store
        if self.collection_name is None:
            self.collection_name = os.environ.get(
                f"{self.object_name.upper()}_COLLECTION",
                settings[f"mongodb.{self.object_name.lower()}_collection"],
            )
        self.collection = getattr(store.database, self.collection_name)

    def get_indexes(self) -> list[IndexModel]:
        # Making multiple indexes with the same unique key is supposed to be impossible
        # https://jira.mongodb.org/browse/SERVER-25023
        # and https://docs.mongodb.com/manual/core/index-partial/#restrictions
        # ``In MongoDB, you cannot create multiple versions of an index that differ only in the options.
        #   As such, you cannot create multiple partial indexes that differ only by the filter expression.``
        # Hold my 🍺
        test_by_public_modified = IndexModel(
            [("public_modified", ASCENDING), ("existing_key", ASCENDING)],
            name="test_by_public_modified",
            partialFilterExpression={
                "is_test": True,
                "is_public": True,
            },
        )
        real_by_public_modified = IndexModel(
            [("public_modified", ASCENDING)],
            name="real_by_public_modified",
            partialFilterExpression={
                "is_test": False,
                "is_public": True,
            },
        )
        all_by_public_modified = IndexModel(
            [
                ("public_modified", ASCENDING),
                ("surely_existing_key", ASCENDING),
            ],  # makes key unique https://jira.mongodb.org/browse/SERVER-25023
            name="all_by_public_modified",
            partialFilterExpression={
                "is_public": True,
            },
        )
        return [
            test_by_public_modified,
            real_by_public_modified,
            all_by_public_modified,
        ]

    async def create_indexes(self) -> None:
        indexes = self.get_indexes()
        # self.collection.drop_indexes()
        # index management probably shouldn't be a part of api initialization
        # a command like `migrate_db` could be called once per release
        # that can manage indexes and data migrations
        # for now I leave it here
        if indexes:
            await self.collection.create_indexes(indexes)

    async def save(self, obj: SaveDataT, insert=False, modified=True) -> SaveDataT:
        data = obj.model_dump(mode="json", warnings=False)
        update = await self.store.save_data(self.collection, data, insert=insert, modified=modified)
        update_obj = obj.model_copy(update=update)
        return update_obj

    async def get(self, uid):
        # if a client doesn't use SESSION cookie, reading from primary solves the issues.
        # So client should use the cookie.
        doc = await self.store.get(self.collection, uid)
        return doc

    async def list(self, **kwargs):
        result = await self.store.list(self.collection, **kwargs)
        return result

    async def flush(self):
        await self.store.flush(self.collection)

    async def delete(self, uid):
        result = await self.store.delete(self.collection, uid)
        return result

    async def find(self, filters: Dict[str, Any]):
        # if a client doesn't use SESSION cookie, reading from primary solves the issues.
        # So client should use the cookie.
        doc = await self.store.find(self.collection, filters)
        return doc


class SequencesCollection(BaseCollection):
    object_name = "sequences"
    collection_name = "sequences"

    async def get_next_value(self, uid):
        result = await self.collection.find_one_and_update(
            {"_id": uid},
            {"$inc": {"value": 1}},
            return_document=ReturnDocument.AFTER,
            upsert=True,
            session=get_db_session_async(),
        )
        return result["value"]

    def get_indexes(self) -> list[IndexModel]:
        return []


def get_mongodb() -> MongodbStore:
    return MongodbStore.get_instance()


session_var: ContextVar[AsyncIOMotorClientSession] = ContextVar("session")


def get_db_session_async() -> AsyncIOMotorClientSession:
    return session_var.get()


def set_db_session_async(db_session) -> Token:
    return session_var.set(db_session)


def reset_db_session_async(token: Token) -> None:
    return session_var.reset(token)


@asynccontextmanager
async def atomic_transaction_async():
    db = get_mongodb().database
    session = get_db_session_async()
    async with session.start_transaction(
        read_preference=db.read_preference,
        write_concern=db.write_concern,
        read_concern=db.read_concern,
    ):
        yield session
