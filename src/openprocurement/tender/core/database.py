from openprocurement.api.constants import RELEASE_2020_04_19
from pymongo import IndexModel, ASCENDING
from pymongo.errors import CollectionInvalid
import logging
import os

logger = logging.getLogger(__name__)


class TenderCollection:

    # complaint_collection_name = "complaints_by_id"

    def __init__(self, store, settings):
        self.store = store
        collection_name = os.environ.get("TENDER_COLLECTION", settings["mongodb.tender_collection"])
        self.collection = getattr(store.database, collection_name)
        # Making multiple indexes with the same unique key is supposed to be impossible
        # https://jira.mongodb.org/browse/SERVER-25023
        # and https://docs.mongodb.com/manual/core/index-partial/#restrictions
        # ``In MongoDB, you cannot create multiple versions of an index that differ only in the options.
        #   As such, you cannot create multiple partial indexes that differ only by the filter expression.``
        # Hold my 🍺
        test_by_public_modified = IndexModel(
            [("public_modified", ASCENDING),
             ("existing_key", ASCENDING)],
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
            [("public_modified", ASCENDING),
             ("surely_existing_key", ASCENDING)],  # makes key unique https://jira.mongodb.org/browse/SERVER-25023
            name="all_by_public_modified",
            partialFilterExpression={
                "is_public": True,
            },
        )

        tender_complaints = IndexModel(
            [("complaints.complaintID", ASCENDING)],
            name="tender_complaints",
            partialFilterExpression={
                "dateCreated": {"$gt": RELEASE_2020_04_19.isoformat()},
            },
        )
        indexes = [
            test_by_public_modified,
            real_by_public_modified,
            all_by_public_modified,

            tender_complaints,
        ]
        for sub_type in ('qualifications', 'awards', 'cancellations'):
            indexes.append(
                IndexModel(
                    [(f"{sub_type}.complaints.complaintID", ASCENDING)],
                    name=f"{sub_type}_complaints",
                    partialFilterExpression={
                        "dateCreated": {"$gt": RELEASE_2020_04_19.isoformat()},
                    },
                )
            )
        # self.collection.drop_indexes()  # TODO: comment me
        # index management probably shouldn't be a part of api initialization
        # a command like `migrate_db` could be called once per release
        # that can manage indexes and data migrations
        # for now I leave it here
        self.collection.create_indexes(indexes)

    def save(self, data, insert=False):
        self.store.save_data(self.collection, data, insert=insert)

    def get(self, uid):
        doc = self.store.get(self.collection, uid)
        return doc

    def list(self, **kwargs):
        result = self.store.list(self.collection, **kwargs)
        return result

    def flush(self):
        self.store.flush(self.collection)
        # self.store.database.drop_collection(self.complaint_collection_name)

    def delete(self, uid):
        self.store.delete(self.collection, uid)

    def find_complaints(self, complaint_id: str):
        collection = self.collection
        query = {
            "complaints": {
                "$elemMatch": {"complaintID": complaint_id}
            },
            "dateCreated": {"$gt": RELEASE_2020_04_19.isoformat()},
        }
        result = collection.find_one(query)
        if result:
            return self._prepare_complaint_response(result, complaint_id)

        for sub_type in ('qualifications', 'awards', 'cancellations'):
            query = {
                "dateCreated": {"$gt": RELEASE_2020_04_19.isoformat()},
                sub_type: {"$elemMatch": {"complaints": {"$elemMatch": {"complaintID": complaint_id}}}},
            }
            result = collection.find_one(query)
            if result:
                return self._prepare_complaint_response(result, complaint_id, item_type=sub_type)
        return []

    @staticmethod
    def _prepare_complaint_response(tender, complaint_id, item_type=None):
        response = [
            {
                "params": {
                    "tender_id": tender["_id"],
                    "item_type": item_type,
                    "item_id": i.get("id"),
                    "complaint_id": c["id"],
                },
                "access": {
                    "token": c["owner_token"]
                }
            }
            for i in (tender[item_type] if item_type else [tender])
            for c in i.get("complaints", "")
            if c["complaintID"] == complaint_id
            # pymongo.errors.OperationFailure: Cannot use $elemMatch projection on a nested field
        ]
        return response
