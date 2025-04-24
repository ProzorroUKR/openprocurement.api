import inspect
import json
import logging
import os
import time
from argparse import ArgumentParser
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Optional, Type

from mock import MagicMock, patch
from pymongo import UpdateOne
from pymongo.collection import Collection
from pymongo.errors import BulkWriteError, OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR
from openprocurement.api.database import (
    MongodbStore,
    get_public_modified,
    get_public_ts,
)
from openprocurement.api.procedure.utils import generate_revision, get_revision_changes
from openprocurement.api.utils import CustomJSONEncoder, get_now

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


MIGRATION_CHANGE_AUTHOR = "migration"
DEFAULT_BATCH_SIZE = 1000


@dataclass
class MigrationResult:
    """Result of a migration operation"""

    updated: int
    failed: int
    processed: int

    def __init__(self, updated: int = 0, failed: int = 0, processed: int = 0):
        self.updated = updated
        self.failed = failed
        self.processed = processed

    def __add__(self, other: 'MigrationResult') -> 'MigrationResult':
        """Add two MigrationResult instances together.

        :param other: Another MigrationResult instance
        :return: New MigrationResult with summed values
        """
        return MigrationResult(
            updated=self.updated + other.updated,
            failed=self.failed + other.failed,
            processed=self.processed + other.processed,
        )


class BaseMigration:
    """Base class for database migrations"""

    def __init__(self, env: Any, args: Any):
        """Initialize migration.

        :param env: Pyramid environment
        :param args: Command line arguments
        """
        self.env = env
        self.args = args

    def run(self) -> None:
        raise NotImplementedError("Subclasses must implement run")


class CollectionMigration(BaseMigration):
    """Base class for database migrations with configurable collection, filter and update logic.

    :ivar description: Description of the migration
    :ivar log_every: Log progress every N records
    :ivar bulk_max_size: Maximum size of bulk operations
    :ivar collection_name: Name of the MongoDB collection to migrate
    """

    description: str = "Base migration"

    collection_name: str = None

    append_revision: bool = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def run(self) -> None:
        """Run the migration."""
        logger.info("Starting migration %s: %s", self.get_name(), self.description)

        try:
            with self._collection.database.client.start_session() as session:
                cursor = self._collection.find(self._filter, self._projection, no_cursor_timeout=True, session=session)
                cursor.batch_size(self.args.b)
                self.process_data(cursor)

        except Exception as e:
            logger.exception(f"Migration failed with error: {type(e).__name__}: {str(e)}", exc_info=e)
            raise
        finally:
            if "cursor" in locals():
                cursor.close()

    def get_name(self) -> str:
        """Get migration name from filename.

        :return: Migration name
        """
        return os.path.basename(inspect.getfile(self.__class__)).split(".")[0]

    def get_collection(self) -> Collection:
        """Get MongoDB collection.

        :return: MongoDB collection
        """
        return getattr(self.env["registry"].mongodb, self.collection_name).collection

    @property
    def _collection(self) -> Collection:
        collection = self.get_collection()
        if self.args.readonly:
            collection = ReadonlyCollectionWrapper(collection)
        if self.args.log:
            collection = LoggingCollectionWrapper(collection)
        return collection

    def get_filter(self) -> dict:
        """Get filter for documents to process.

        :return: MongoDB filter query
        """
        return {}

    @property
    def _filter(self) -> dict:
        filter = self.get_filter()
        if self.args.filter:
            filter.update(json.loads(self.args.filter))
        return filter

    def get_projection(self) -> dict:
        """Get projection for documents to process.

        :return: MongoDB projection
        """
        return {}

    @property
    def _projection(self) -> dict:
        projection = self.get_projection()
        if projection:
            # if projection is set, add additional fields required for migration,
            # else all fields will be present
            projection.update({"_id": 1, "_rev": 1})
            if self.append_revision:
                projection.update({"revisions": 1})
        return projection

    def update_document(self, doc: dict) -> Optional[UpdateOne]:
        """Process a single document.

        :param doc: Document to process
        :return: UpdateOne operation if document needs to be updated, None otherwise
        :raises NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError("Subclasses must implement process_document")

    def process_operation(self, doc: dict) -> UpdateOne:
        """Generate update operation for a single document.

        :param pipeline: Pipeline of update operations
        :return: UpdateOne operation
        """
        pipeline = self.process_pipeline(doc)

        if not pipeline:
            # Skip document processing
            return None

        return UpdateOne(
            {"_id": doc["_id"], "_rev": doc["_rev"]},
            pipeline,
        )

    def process_pipeline(self, doc: dict) -> dict:
        """Generate update pipeline for a single document.

        :param doc: Original document
        :return: UpdateOne operation
        """

        updated_doc = deepcopy(doc)
        updated_doc = self.update_document(updated_doc)

        if not updated_doc or doc == updated_doc:
            # Skip document processing
            return None

        if self.append_revision:
            self.validate_revisions_update(doc, updated_doc)
            patch = get_revision_changes(updated_doc, doc)
            if patch:
                revision = generate_revision(updated_doc, patch, MIGRATION_CHANGE_AUTHOR, get_now())
                updated_doc["revisions"].append(revision)

        pipeline = []
        pipeline.extend(self.generate_base_pipeline_stages(updated_doc))
        pipeline.extend(self.generate_revision_number_pipeline_stages(updated_doc))

        if self.update_date_modified:
            pipeline.extend(self.generate_date_modified_pipeline_stages(updated_doc))

        if self.update_feed_position:
            pipeline.extend(self.generate_feed_position_pipeline_stages(updated_doc))

        return pipeline

    def generate_base_pipeline_stages(self, doc: dict) -> dict:
        return [
            {"$set": doc},
        ]

    def generate_revision_number_pipeline_stages(self, doc: dict) -> dict:
        return [
            {"$set": {"_rev": MongodbStore.get_next_rev(doc["_rev"])}},
        ]

    def generate_date_modified_pipeline_stages(self, doc: dict) -> dict:
        return [
            {"$set": {"dateModified": get_now().isoformat()}},
        ]

    def generate_feed_position_pipeline_stages(self, doc: dict) -> dict:
        return [
            {
                "$set": {
                    "public_modified": get_public_modified(),
                    "public_ts": get_public_ts(),
                }
            },
        ]

    def validate_revisions_update(self, doc: dict, updated_doc: dict) -> None:
        revisions = doc.get("revisions")
        revisions_future = updated_doc.get("revisions")
        if not revisions or not revisions_future or revisions != revisions_future:
            raise ValueError("Document has no revisions. Revisions may be lost. Please check the projection.")

    def process_data(self, cursor) -> MigrationResult:
        """Process documents from cursor and apply updates.

        :param cursor: MongoDB cursor with documents to process
        :return: MigrationResult containing counts of updated, failed and processed documents
        """
        bulk = []

        result = MigrationResult()

        for doc in cursor:
            result.processed += 1

            update_operation = None
            try:
                update_operation = self.process_operation(doc)
            except Exception as e:
                result.failed += 1
                logger.exception(
                    f"Failed to process document {doc.get('_id')}. {type(e).__name__}: {str(e)}",
                    exc_info=e,
                )
                continue

            if not update_operation:
                # Skip document processing
                continue

            bulk.append(update_operation)

            if bulk and len(bulk) % self.bulk_max_size == 0:
                bulk_result = self.process_bulk(bulk)
                result += bulk_result

                bulk = []

                if result.processed % self.log_every == 0:
                    logger.info(f"Updated documents: {result.processed}")

        if bulk:
            bulk_result = self.process_bulk(bulk)
            result += bulk_result

        self._log_result(result)
        return result

    def _log_result(self, result: MigrationResult) -> None:
        """Log migration results.

        :param result: Migration result to log
        """
        logger.info(
            f"Finished migration {self.get_name()}: {self.description} - "
            f"updated {result.updated} documents, failed {result.failed} documents, "
            f"total processed {result.processed}"
        )

    def process_bulk(self, bulk: list[UpdateOne]) -> MigrationResult:
        """Process a batch of updates, falling back to one-by-one processing if bulk fails.

        :param bulk: List of UpdateOne operations
        :return: Tuple of (successfully updated count, failed count)
        """
        try:
            self._collection.bulk_write(bulk)
            return MigrationResult(updated=len(bulk))
        except (OperationFailure, BulkWriteError) as e:
            logger.exception(
                f"Bulk operation failed, switching to one-by-one processing. {type(e).__name__}: {str(e)}",
                exc_info=e,
            )
            return self.process_alternately(bulk)

    def process_alternately(self, bulk: list[UpdateOne]) -> MigrationResult:
        """Process each update operation individually with retries.

        :param bulk: List of UpdateOne operations
        :return: Tuple of (successfully updated count, failed count)
        """
        result = MigrationResult()

        max_retries = 3
        retry_delay = 1  # seconds

        for operation in bulk:
            doc_id = operation._filter["_id"]
            success = False

            for attempt in range(max_retries):
                try:
                    # Refetch the document to get latest version
                    doc = self._collection.find_one({"_id": doc_id}, self._projection)
                    if not doc:
                        logger.error(f"Document {doc_id} not found")
                        result.failed += 1
                        break

                    # Reapply update logic
                    try:
                        pipeline = self.process_pipeline(doc)
                    except Exception as e:
                        logger.exception(
                            f"Failed to process document {doc_id}. {type(e).__name__}: {str(e)}",
                            exc_info=e,
                        )
                        result.failed += 1
                        break

                    if not pipeline:
                        # Skip document processing
                        break

                    # Update document with latest changes
                    self._collection.update_one({"_id": doc_id, "_rev": doc["_rev"]}, pipeline)
                    result.updated += 1
                    success = True
                    break
                except OperationFailure as e:
                    if attempt == max_retries - 1:
                        logger.exception(
                            f"Failed to update document {doc_id} after {max_retries} attempts. {type(e).__name__}: {str(e)}",
                            exc_info=e,
                        )
                        result.failed += 1
                    else:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for document {doc_id}. "
                            f"Retrying in {retry_delay} seconds. Error: {str(e)}"
                        )
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff

            if success:
                retry_delay = 1  # Reset retry delay for next document

        return result

    def run_test_mock(self, mock_collection):
        with patch.object(self, 'get_collection', return_value=mock_collection):
            self.run()

    def run_test_data(self, test_docs: list[dict]):
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter(test_docs)

        mock_collection = MagicMock()
        mock_collection.database = self._collection.database
        mock_collection.find.return_value = mock_cursor

        self.run_test_mock(mock_collection)

        return mock_collection


class LoggingCollectionJSONEncoder(CustomJSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return str(obj)
        return super().default(obj)


class LoggingCollectionWrapper:
    json_encoder = LoggingCollectionJSONEncoder

    def __init__(self, collection):
        self._collection = collection
        self._logger = logger

    def __getattr__(self, name):
        attr = getattr(self._collection, name)

        if not callable(attr):
            return attr

        def wrapper(*args, **kwargs):
            if name == 'bulk_write':
                ops_original = args[0]
                for op in ops_original:
                    op_args = []
                    op_parent_class = op.__class__.__bases__[0]
                    for slot in op_parent_class.__slots__:
                        op_args.append(getattr(op, slot))
                    op_name = op.__class__.__name__
                    self._logger.info(f"{name}([{op_name}({self.dumps(op_args)})])")
            else:
                self._logger.info(f"{name}({self.dumps(args)}, {self.dumps(kwargs)})")
            return attr(*args, **kwargs)

        return wrapper

    def dumps(self, obj):
        return json.dumps(obj, indent=2, ensure_ascii=False, cls=self.json_encoder)


class ReadonlyCollectionWrapper:
    """Wrapper that simulates database writes in readonly mode."""

    write_methods = (
        'update_one',
        'update_many',
        'bulk_write',
        'insert_one',
        'insert_many',
        'delete_one',
        'delete_many',
    )

    def __init__(self, collection):
        self._collection = collection
        self._logger = logger

    def __getattr__(self, name):
        attr = getattr(self._collection, name)

        if not callable(attr):
            return attr

        def wrapper(*args, **kwargs):
            if name in self.write_methods:
                self._logger.info(f"Working in readonly mode, imitating execution of {name}")
                return {}
            return attr(*args, **kwargs)

        return wrapper


class BaseMigrationArgumentParser(ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument(
            "-p",
            default=os.path.join(BASE_DIR, "etc/service.ini"),
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


class CollectionMigrationArgumentParser(BaseMigrationArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument(
            "--test",
            action="store_true",
            help=("Run the migration in test mode."),
        )
        self.add_argument(
            "--log",
            action="store_true",
            help=("Log all operations."),
        )
        self.add_argument(
            "--readonly",
            action="store_true",
            help=("Run migration in readonly mode - all database writes will be simulated."),
        )
        self.add_argument(
            "--filter",
            help=("Filter for documents to process."),
        )


def migrate(
    migration: Type[BaseMigration],
    parser: Type[BaseMigrationArgumentParser] = BaseMigrationArgumentParser,
):
    os.environ["NO_GEVENT_MONKEY_PATCH"] = "1"
    args = parser().parse_args()
    with bootstrap(args.p) as env:
        if args.test:
            migration(env, args).run_test()
        else:
            migration(env, args).run()


def migrate_collection(
    migration: Type[CollectionMigration],
    parser: Type[CollectionMigrationArgumentParser] = CollectionMigrationArgumentParser,
):
    migrate(migration, parser)


if __name__ == "__main__":
    migrate(BaseMigration)
