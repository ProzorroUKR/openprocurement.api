import asyncio
import logging
from typing import Any, Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne

from openprocurement.api.migrations.base import (
    CollectionMigration,
    CollectionMigrationArgumentParser,
    MigrationResult,
    init_migration,
)
from prozorro_cdb.api.database.store import (
    MongodbStore,
    atomic_transaction_async,
    get_public_modified,
    reset_db_session_async,
    set_db_session_async,
)

logger = logging.getLogger(__name__)


class AsyncIOMotorCollectionMigration(CollectionMigration):
    """Async collection migration using motor (AsyncIOMotorCollection)."""

    description: str = "async mongodb collection migration"

    collection_name: str
    db_store: MongodbStore

    append_revision: bool = False
    update_date_modified: bool = False
    update_feed_position: bool = False

    def __init__(self, settings: dict = None, args: Any = None):
        super().__init__(settings, args)
        self.db_store = MongodbStore.create_instance(settings)

    def get_collection(self) -> AsyncIOMotorCollection:
        """Get MongoDB collection.

        :return: MongoDB collection
        """
        return self.db_store.database.get_collection(self.collection_name)

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return self.get_collection()

    def update_document(self, doc: dict, context: dict = None) -> Optional[dict]:
        """Process a single document.

        :param doc: dict of document to process
        :param context: dict of context
        :return: dict of modified document needs to be updated, None otherwise
        :raises NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError("Subclasses must implement update_document")

    def get_next_revision(self, doc: dict) -> str:
        return self.db_store.get_next_rev(doc["_rev"])

    def generate_feed_position_pipeline_stages(self, doc: dict) -> list[dict]:
        """Override to use prozorro_cdb store (no public_ts)."""
        return [{"$set": {"public_modified": get_public_modified()}}]

    async def bulk_update(self, batch: list) -> int:
        """Execute bulk write, return number of updated documents."""
        async with await self.db_store.connection.start_session() as s:
            token = set_db_session_async(s)
            try:
                async with atomic_transaction_async() as session:
                    result = await self.collection.bulk_write(batch, session=session)
                    if result.modified_count != len(batch):
                        logger.error(f"Unexpected modified_count: {result.modified_count}; expected {len(batch)}")
                    return result.modified_count
            finally:
                reset_db_session_async(token)

    def process_operation(self, doc: dict, context: dict = None) -> Optional[UpdateOne]:
        """Generate update operation for a single document.

        :param pipeline: Pipeline of update operations
        :param context: dict of context
        :return: UpdateOne operation
        """
        pipeline = self.process_pipeline(doc, context=context)

        if not pipeline:
            # Skip document processing
            return None

        return UpdateOne(
            {"_id": doc["_id"], "_rev": doc["_rev"]},
            pipeline,
        )

    async def process_data(self, cursor) -> MigrationResult:
        """Process documents from cursor and apply updates.

        :param cursor: Async MongoDB cursor with documents to process
        :return: MigrationResult containing counts of updated, failed and processed documents
        """
        bulk = []
        result = MigrationResult()
        context = {}

        async for doc in cursor:
            result.processed += 1

            update_operation = self.process_operation(doc, context=context)
            if update_operation:
                bulk.append(update_operation)

            if bulk and len(bulk) % self.args.b == 0:
                result.updated += await self.bulk_update(bulk)
                bulk = []
                if result.processed % self.log_every == 0:
                    self.log_result(result)

        if bulk:
            result.updated += await self.bulk_update(bulk)

        return result

    def log_result(self, result: MigrationResult, action: str = "Processing") -> None:
        logger.info(
            f"{action} migration {self.collection.name}: {self.description} - "
            f"updated {result.updated} documents, failed {result.failed} documents, "
            f"total processed {result.processed}"
        )

    async def run(self):
        logger.info("Starting %s collection migration %s: %s ", self.collection.name, self.get_name(), self.description)

        cursor = self.collection.find(self.filter, projection=self.projection)
        result = await self.process_data(cursor)

        self.log_result(result, action="Finished")


def migrate_collection(
    migration: Type[AsyncIOMotorCollectionMigration],
    parser: Type[CollectionMigrationArgumentParser] = CollectionMigrationArgumentParser,
):
    migration_instance = init_migration(migration, parser)
    asyncio.run(migration_instance.run())
