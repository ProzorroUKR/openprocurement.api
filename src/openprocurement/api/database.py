import os
from contextlib import contextmanager
from decimal import Decimal
from logging import getLogger
from time import monotonic
from uuid import uuid4

from bson.codec_options import CodecOptions, TypeCodec, TypeRegistry
from bson.decimal128 import Decimal128
from pymongo import (
    ASCENDING,
    DESCENDING,
    IndexModel,
    MongoClient,
    ReadPreference,
    ReturnDocument,
)
from pymongo.monitoring import CommandListener
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from openprocurement.api.context import get_db_session, get_request, get_request_now
from openprocurement.api.exceptions import MongodbResourceConflict
from openprocurement.api.utils import update_logging_context

LOGGER = getLogger("{}.init".format(__name__))


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
    ]
)
codec_options = CodecOptions(type_registry=type_registry)


# How many seconds behind "now" the forward feed lags.
# Prevents race conditions where $$NOW is captured at operation start,
# not at commit time — concurrent writes can commit out-of-order and
# permanently disappear from the feed for crawlers.
# Uses MongoDB's own $$NOW to avoid clock drift between API and DB servers.
# See: docs/source/developers/projects/cdb/feed_ordering.rst
FEED_WATERMARK_SECONDS = int(os.environ.get("FEED_WATERMARK_SECONDS", "1"))

# Transactions longer than this are logged with MESSAGE_ID "transaction_duration_exceeded".
# public_modified ($$NOW) is fixed at save_data statement, but the document becomes visible
# only at commit. If this gap exceeds FEED_WATERMARK_SECONDS, the document can be skipped
# by feed crawlers. See: docs/source/developers/projects/cdb/feed_ordering.rst
TRANSACTION_DURATION_WARNING_SECONDS = float(
    os.environ.get("TRANSACTION_DURATION_WARNING_SECONDS", FEED_WATERMARK_SECONDS / 2)
)

# Non-transactional save_data (update_one) longer than this is logged with
# MESSAGE_ID "save_data_duration_exceeded". Same reason: $$NOW is fixed at the operation start,
# but the write can wait (another transaction holding the document, WiredTiger tickets, eviction)
# and become visible much later. See: docs/source/developers/projects/cdb/feed_ordering.rst
SAVE_DATA_DURATION_WARNING_SECONDS = float(
    os.environ.get("SAVE_DATA_DURATION_WARNING_SECONDS", FEED_WATERMARK_SECONDS / 2)
)


def get_public_modified():
    public_modified = {"$divide": [{"$toLong": "$$NOW"}, 1000]}
    return public_modified


def get_public_ts():
    return "$$CLUSTER_TIME"


class MongoServerLoggingListener(CommandListener):
    @staticmethod
    def _format_mongo_server(connection_id):
        """Format (host, port) as 'host:port' for logging."""
        host, port = connection_id[0], connection_id[1]
        return f"{host}:{port}" if port is not None else str(host)

    @staticmethod
    def _mongo_settings(store):
        database = store.database
        return {
            "DB_NAME": database.name,
            "READ_PREFERENCE": database.read_preference.name,
            "WRITE_CONCERN": str(database.write_concern.document),
            "READ_CONCERN": database.read_concern.level,
        }

    @staticmethod
    def _replica_info_from_topology(store, connection_id):
        client = store.connection
        topo = client.topology_description
        sds = topo.server_descriptions()

        host, port = connection_id[0], connection_id[1]
        for addr, sdesc in sds.items():
            if addr[0] == host and addr[1] == port:
                out = {
                    "SERVER_TYPE": sdesc.server_type_name,
                    "RTT_SEC": sdesc.round_trip_time or sdesc.min_round_trip_time,
                }
                return out

        return {}

    def _update_logging_context(self, event):
        if event.connection_id is None:
            return

        request = get_request()
        if request is None:
            return

        params = {"SERVER": self._format_mongo_server(event.connection_id)}

        store = getattr(request.registry, "mongodb", None)
        if store:
            try:
                params.update(self._replica_info_from_topology(store, event.connection_id))
                params.update(self._mongo_settings(store))
            except (AttributeError, TypeError):
                LOGGER.warning("Failed to get mongo settings from store for logging context", exc_info=True)

        update_logging_context(request, {"MONGO_LAST_COMMAND_INFO": params})

    def started(self, event):
        pass

    def succeeded(self, event):
        self._update_logging_context(event)

    def failed(self, event):
        self._update_logging_context(event)


class MongodbStore:
    def __init__(self, settings):
        self.settings = settings
        self.collections = {}

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
        self.connection = MongoClient(
            mongodb_uri,
            maxPoolSize=max_pool_size,
            minPoolSize=min_pool_size,
            event_listeners=[MongoServerLoggingListener()],
        )
        self.database = self.connection.get_database(
            db_name,
            read_preference=getattr(ReadPreference, raw_read_preference),
            write_concern=WriteConcern(w=int(raw_w_concert) if raw_w_concert.isnumeric() else raw_w_concert),
            read_concern=ReadConcern(level=raw_r_concern),
            codec_options=codec_options,
        )

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
        raise AttributeError(f"MongodbStore has no attribute {name}")

    def add_collection(self, name, cls):
        self.collections[name] = cls(self, self.settings)

    def get_sequences_collection(self):
        return self.database.sequences

    def get_next_sequence_value(self, uid):
        collection = self.get_sequences_collection()
        result = collection.find_one_and_update(
            {"_id": uid},
            {"$inc": {"value": 1}},
            return_document=ReturnDocument.AFTER,
            upsert=True,
            session=get_db_session(),
        )
        return result["value"]

    def flush_sequences(self):
        collection = self.get_sequences_collection()
        self.flush(collection)

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
    def get(collection, uid, first_revision_only=False):
        projection = {
            "is_public": False,
            "is_test": False,
        }
        if first_revision_only:
            # read-only requests need only the first revision (get_first_revision_date),
            # so the whole history is neither transferred nor decoded
            projection["revisions"] = {"$slice": 1}
        res = collection.find_one(
            {"_id": uid},
            projection=projection,
            session=get_db_session(),
        )
        return res

    def list(
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

        if offset_field == "public_modified" and FEED_WATERMARK_SECONDS > 0 and (not descending or not offset_value):
            # Watermark: exclude records newer than FEED_WATERMARK_SECONDS.
            # $$NOW is evaluated by MongoDB itself — no cross-server clock drift.
            # Skipped when FEED_WATERMARK_SECONDS=0 (e.g. in tests via monkeypatch).
            #
            # Applied to:
            #   - forward feed (not descending): always, to prevent crawlers from
            #     advancing past records that haven't committed yet.
            #   - descending feed WITHOUT offset (first page only): to guarantee that
            #     pm_max used as a forward-sync starting point is old enough that all
            #     concurrent writes with $$NOW <= pm_max have already committed.
            #     Without this, backward→forward sync can permanently miss records
            #     that were in-flight during the initial descending read.
            #   - descending WITH offset: skipped — paginating through historical data,
            #     no race condition possible for already-committed old records.
            filters["$expr"] = {
                "$lte": [
                    f"${offset_field}",
                    {
                        "$subtract": [
                            {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                            FEED_WATERMARK_SECONDS,
                        ]
                    },
                ]
            }

        results = list(
            collection.find(
                filter=filters,
                projection={f: 1 for f in fields},
                limit=limit,
                sort=((offset_field, DESCENDING if descending else ASCENDING),),
                session=get_db_session(),
            )
        )
        for e in results:
            self.rename_id(e)
        return results

    def save_data(self, collection, data, insert=False, modified=True):
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
        if insert:
            data["dateCreated"] = get_request_now().isoformat()
        if modified:
            data["dateModified"] = get_request_now().isoformat()
            pipeline.append(
                {
                    "$set": {
                        "public_modified": get_public_modified(),
                        "public_ts": get_public_ts(),  # create items to migrate
                    }
                }
            )
        session = get_db_session()
        started_at = monotonic()
        # update_one instead of find_one_and_update: the previous document is not needed,
        # so mongodb doesn't have to serialize and send the whole document back
        result = collection.update_one(
            {"_id": uid, "_rev": revision},
            pipeline,
            upsert=insert,
            session=session,
        )
        duration = monotonic() - started_at
        if not result.modified_count and not result.upserted_id:
            raise MongodbResourceConflict("Conflict while updating document. Please, retry")
        # inside a transaction the document becomes visible only at commit,
        # that case is covered by atomic_transaction -> log_transaction_duration
        if modified and not (session and session.in_transaction):
            log_save_data_duration(collection.name, uid, duration)
        return data

    def save_data_simple(self, collection, data, insert=False):
        uid = data.pop("id" if "id" in data else "_id")
        data["_id"] = uid
        if insert:
            collection.insert_one(data)
        else:
            result = collection.replace_one(
                {"_id": uid},
                data,
                session=get_db_session(),
            )
            if result.matched_count == 0:
                raise MongodbResourceConflict("Unable to find the object")
        return data

    @staticmethod
    def flush(collection):
        result = collection.delete_many({})
        return result

    @staticmethod
    def delete(collection, uid):
        result = collection.delete_one({"_id": uid}, session=get_db_session())
        return result

    @staticmethod
    def rename_id(obj):
        if obj:
            obj["id"] = obj.pop("_id")
        return obj


class BaseCollection:
    object_name = "dummy"

    def __init__(self, store, settings):
        self.store = store
        collection_name = os.environ.get(
            f"{self.object_name.upper()}_COLLECTION",
            settings[f"mongodb.{self.object_name.lower()}_collection"],
        )
        self.collection = getattr(store.database, collection_name)
        if isinstance(self.collection.read_preference, type(ReadPreference.PRIMARY)):
            self.collection_primary = self.collection
        else:
            self.collection_primary = self.collection.with_options(read_preference=ReadPreference.PRIMARY)
        self.create_indexes()

    def get_indexes(self):
        public_modified_index = IndexModel(
            [
                ("public_modified", ASCENDING),
            ],
            name="public_modified",
        )
        real_by_public_modified_index = IndexModel(
            [
                ("public_modified", ASCENDING),
            ],
            name="real_by_public_modified",
            partialFilterExpression={
                "is_test": False,
                "is_public": True,
            },
        )
        test_by_public_modified_index = IndexModel(
            [
                ("public_modified", ASCENDING),
                ("existing_key", ASCENDING),
                # this hack key was used to allow index with the same fields
                # but different partial index filters
                # https://jira.mongodb.org/browse/SERVER-25023
                # this is not required anymore
                # but we keep it so we don't need to recreate the existing indexes
            ],
            name="test_by_public_modified",
            partialFilterExpression={
                "is_test": True,
                "is_public": True,
            },
        )
        all_by_public_modified_index = IndexModel(
            [
                ("public_modified", ASCENDING),
                ("surely_existing_key", ASCENDING),
                # this hack key was used to allow index with the same fields
                # but different partial index filters
                # https://jira.mongodb.org/browse/SERVER-25023
                # this is not required anymore
                # but we keep it so we don't need to recreate the existing indexes
            ],
            name="all_by_public_modified",
            partialFilterExpression={
                "is_public": True,
            },
        )
        return [
            public_modified_index,
            real_by_public_modified_index,
            test_by_public_modified_index,
            all_by_public_modified_index,
        ]

    def create_indexes(self):
        indexes = self.get_indexes()
        # self.collection.drop_indexes()
        # index management probably shouldn't be a part of api initialization
        # a command like `migrate_db` could be called once per release
        # that can manage indexes and data migrations
        # for now I leave it here
        self.collection.create_indexes(indexes)

    def save(self, o, insert=False, modified=True):
        data = o.to_primitive()
        updated = self.store.save_data(self.collection, data, insert=insert, modified=modified)
        o.import_data(updated)

    def get(self, uid, first_revision_only=False):
        # if a client doesn't use SESSION cookie
        # reading from primary solves the issues
        # when write operation is allowed because of a state object from a secondary replica
        # This means more reads from Primary, but at the moment we can't force everybody to use the cookie
        # ! There is also the case, that internal services (like chronograph or tasks)
        # can read stale versions from secondaries !
        collection = (
            self.collection if getattr(get_request(), "method", None) in ("GET", "HEAD") else self.collection_primary
        )
        doc = self.store.get(collection, uid, first_revision_only=first_revision_only)
        return doc

    def list(self, **kwargs):
        result = self.store.list(self.collection, **kwargs)
        return result

    def flush(self):
        self.store.flush(self.collection)

    def delete(self, uid):
        result = self.store.delete(self.collection, uid)
        return result


@contextmanager
def atomic_transaction(enabled=True):
    s = get_db_session()
    if not enabled:
        yield s
        return
    request = get_request()
    database = request.registry.mongodb.database
    started_at = monotonic()
    with s.start_transaction(
        # read_preference=database.read_preference,
        write_concern=database.write_concern,
        read_concern=database.read_concern,
    ):
        yield s
        body_finished_at = monotonic()
    # reached only after successful commit (on exception the transaction is aborted)
    committed_at = monotonic()
    log_transaction_duration(
        request,
        body_duration=body_finished_at - started_at,
        commit_duration=committed_at - body_finished_at,
    )


def log_save_data_duration(collection_name, uid, duration):
    """
    Logs a warning if a non-transactional save_data that sets public_modified took too long.

    duration includes waiting for write concern (majority) - replication lag alone
    doesn't break feed ordering, but it can't be separated on the client side
    """
    if duration <= SAVE_DATA_DURATION_WARNING_SECONDS:
        return

    msg = {
        "MESSAGE_ID": "save_data_duration_exceeded",
        "SAVE_DATA_DURATION": round(duration, 3),
        "SAVE_DATA_COLLECTION": collection_name,
        "SAVE_DATA_ID": uid,
    }
    request = get_request()
    if request is not None:
        # pylint: disable-next=import-outside-toplevel, cyclic-import
        from openprocurement.api.utils import context_unpack

        msg = context_unpack(request, msg)

    LOGGER.warning(
        f"save_data {collection_name} {uid} took {duration:.3f}s, "
        f"threshold {SAVE_DATA_DURATION_WARNING_SECONDS}s, "
        f"feed watermark {FEED_WATERMARK_SECONDS}s",
        extra=msg,
    )


def log_transaction_duration(request, body_duration, commit_duration):
    """
    Logs a warning if the transaction took too long.

    body_duration   - time from the transaction start to the end of the `with` block
                      (first save_data statement -> last statement); this is the main
                      source of the public_modified vs commit gap
    commit_duration - commitTransaction call, includes waiting for write concern (majority);
                      waiting for replication doesn't break feed ordering by itself,
                      logged separately to distinguish the causes
    """
    total_duration = body_duration + commit_duration
    if total_duration <= TRANSACTION_DURATION_WARNING_SECONDS:
        return

    # pylint: disable-next=import-outside-toplevel, cyclic-import
    from openprocurement.api.utils import context_unpack

    LOGGER.warning(
        f"Transaction took {total_duration:.3f}s "
        f"(body {body_duration:.3f}s, commit {commit_duration:.3f}s), "
        f"threshold {TRANSACTION_DURATION_WARNING_SECONDS}s, "
        f"feed watermark {FEED_WATERMARK_SECONDS}s",
        extra=context_unpack(
            request,
            {
                "MESSAGE_ID": "transaction_duration_exceeded",
                "TRANSACTION_DURATION": round(total_duration, 3),
                "TRANSACTION_BODY_DURATION": round(body_duration, 3),
                "TRANSACTION_COMMIT_DURATION": round(commit_duration, 3),
            },
        ),
    )
