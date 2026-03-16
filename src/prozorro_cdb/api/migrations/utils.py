import logging
from argparse import ArgumentParser
from copy import deepcopy
from typing import Type

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne

from openprocurement.api.migrations.base import MIGRATION_CHANGE_AUTHOR
from openprocurement.api.procedure.utils import generate_revision, get_revision_changes
from openprocurement.api.utils import get_now
from prozorro_cdb.api.database.store import (
    BaseCollection,
    MongodbStore,
    atomic_transaction_async,
    get_public_modified,
    reset_db_session_async,
    set_db_session_async,
)

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 1000


class BaseMigrationArgumentParser(ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument(
            "-p",
            required=True,
            help="Path to service.ini file",
        )
        self.add_argument(
            "-b",
            type=int,
            default=DEFAULT_BATCH_SIZE,
            help=(
                "Limits the number of documents returned in one batch. Each batch requires a round trip to the server."
            ),
        )


class CollectionMigration:
    collection_cls: Type[BaseCollection]
    db_store: MongodbStore
    collection: AsyncIOMotorCollection

    append_revision: bool = False
    update_date_modified: bool = False
    update_feed_position: bool = False

    def __init__(self, settings: dict = None, batch_size: int = DEFAULT_BATCH_SIZE):
        self.init_db_store(settings)
        self.batch_size = batch_size

    def init_db_store(self, settings: dict = None):
        try:
            self.db_store = MongodbStore.get_instance()
        except RuntimeError:
            settings = settings or dict()
            self.db_store = MongodbStore.create_instance(settings)
        self.db_store.add_collection(
            self.collection_cls.object_name,
            self.collection_cls,
        )
        self.collection = getattr(self.db_store, self.collection_cls.object_name).collection

    def generate_base_pipeline_stages(self, doc: dict) -> list[dict]:
        return [{"$set": doc}]

    def generate_revision_number_pipeline_stages(self, doc: dict) -> list[dict]:
        return [{"$set": {"_rev": MongodbStore.get_next_rev(doc["_rev"])}}]

    def generate_feed_position_pipeline_stages(self, doc: dict) -> list[dict]:
        return [{"$set": {"public_modified": get_public_modified()}}]

    def generate_date_modified_pipeline_stages(self, doc: dict) -> list[dict]:
        return [{"$set": {"dateModified": get_now().isoformat()}}]

    def get_filter(self) -> dict:
        return dict()

    def get_projection(self) -> dict:
        return dict()

    @property
    def _projection(self) -> dict:
        projection = self.get_projection()
        if projection:
            # if projection is set, add additional fields required for migration,
            # else all fields will be present
            projection.update({"_id": 1, "_rev": 1})
            if self.append_revision:
                projection.update({"revisions": 1})
            self.validate_projection(projection)
        return projection

    def update_obj(self, doc: dict) -> dict:
        raise NotImplementedError

    def validate_revisions_update(self, doc: dict, updated_doc: dict):
        revisions = doc.get("revisions")
        revisions_future = updated_doc.get("revisions")
        if not revisions or not revisions_future or revisions != revisions_future:
            raise ValueError("Document has no revisions. Revisions may be lost. Please check the projection.")

    def validate_projection(self, projection: dict):
        """Ensure projection has no nested fields.

        :param projection: MongoDB projection to validate
        :raises ValueError: If any projection key contains "."
        """
        for key in projection:
            if "." in key:
                raise ValueError(f"Nested projection '{key}' is not allowed. Use top-level field names only.")

    async def bulk_update(self, batch: list, counter: int):
        async with await self.db_store.connection.start_session() as s:
            token = set_db_session_async(s)
            try:
                async with atomic_transaction_async() as session:
                    result = await self.collection.bulk_write(batch, session=session)
                    logger.info(f"Processed {counter} docs in {self.collection.name}")
                    if result.modified_count != len(batch):
                        logger.error(f"Unexpected modified_count: {result.modified_count}; expected {len(batch)}")
            finally:
                # without finally
                # in case of exceptions session_var may contain an ended session link
                reset_db_session_async(token)

    async def run(self):
        counter = 0
        batch = []

        logger.info(f"Start {self.collection.name} collection migration")
        async for doc in self.collection.find(self.get_filter(), projection=self._projection):
            updated_doc = self.update_obj(deepcopy(doc))

            # if doc was not changed - skip
            if not updated_doc or updated_doc == doc:
                continue

            if self.append_revision:
                self.validate_revisions_update(doc, updated_doc)
                patch = get_revision_changes(updated_doc, doc)
                if patch:
                    revision = generate_revision(updated_doc, patch, MIGRATION_CHANGE_AUTHOR, get_now())
                    updated_doc["revisions"].append(revision)

            pipelines = []
            pipelines.extend(self.generate_base_pipeline_stages(updated_doc))
            pipelines.extend(self.generate_revision_number_pipeline_stages(updated_doc))

            if self.update_date_modified:
                pipelines.extend(self.generate_date_modified_pipeline_stages(updated_doc))

            if self.update_feed_position:
                pipelines.extend(self.generate_feed_position_pipeline_stages(updated_doc))

            batch.append(
                UpdateOne(
                    {"_id": doc["_id"], "_rev": doc["_rev"]},
                    pipelines,
                )
            )
            counter += 1

            if batch and len(batch) % self.batch_size == 0:
                await self.bulk_update(batch, counter)
                batch = []

        if batch:
            await self.bulk_update(batch, counter)

        logger.info(f"Finished. Processed {counter} objects in {self.collection.name} collection")
        logger.info("Successfully migrated")
