from pymongo import IndexModel, ASCENDING
import os


class PlanCollection:

    def __init__(self, store, settings):
        self.store = store
        collection_name = os.environ.get("PLAN_COLLECTION", settings["mongodb.plan_collection"])
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
        # self.collection.drop_indexes()
        # index management probably shouldn't be a part of api initialization
        # a command like `migrate_db` could be called once per release
        # that can manage indexes and data migrations
        # for now I leave it here
        self.collection.create_indexes([test_by_public_modified, real_by_public_modified, all_by_public_modified])

    def save(self, o, insert=False):
        data = o.to_primitive()
        updated = self.store.save_data(self.collection, data, insert=insert)
        o.import_data(updated)

    def get(self, uid):
        doc = self.store.get(self.collection, uid)
        return doc

    def list(self, **kwargs):
        result = self.store.list(self.collection, **kwargs)
        return result

    def flush(self):
        self.store.flush(self.collection)
