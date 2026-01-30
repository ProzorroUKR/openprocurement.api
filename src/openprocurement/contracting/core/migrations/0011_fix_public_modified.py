import logging

from pymongo import DESCENDING

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Fix public_modified field in tenders"

    collection_name = "tenders"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    def process_data(self, cursor):
        cursor.sort([("public_modified", DESCENDING)])
        super().process_data(cursor)

    def get_filter(self) -> dict:
        return {
            "is_public": True,
            "public_modified": {"$type": "object"},  # Was accidentally saved as object, not a number
        }

    def get_projection(self):
        return {"public_modified": 1}

    def update_document(self, doc, context=None):
        doc["public_modified"] = 1769733297.013  # It will be rewritten by the correct value by the migration engine
        logger.info(f"Fixed public_modified in tender {doc['_id']}")
        return doc


if __name__ == "__main__":
    migrate_collection(Migration)
