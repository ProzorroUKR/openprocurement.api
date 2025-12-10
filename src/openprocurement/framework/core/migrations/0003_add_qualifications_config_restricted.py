import logging
import os

from pymongo.errors import OperationFailure

from openprocurement.api.migrations.base import BaseMigration, migrate

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def restricted_populator(qualification):
    return False


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.qualifications.collection

    logger.info("Updating qualifications with restricted field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.restricted": {"$exists": False}},
        {"config": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for qualification in cursor:
            if qualification.get("config", {}).get("restricted") is None:
                try:
                    collection.update_one(
                        {"_id": qualification["_id"]},
                        {"$set": {"config.restricted": restricted_populator(qualification)}},
                    )
                    count += 1
                    if count % log_every == 0:
                        logger.info(f"Updating qualifications with restricted field: updated {count} qualifications")
                except OperationFailure as e:
                    logger.warning(f"Skip updating qualification {qualification['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(f"Updating qualifications with restricted field finished: updated {count} qualifications")

    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)
