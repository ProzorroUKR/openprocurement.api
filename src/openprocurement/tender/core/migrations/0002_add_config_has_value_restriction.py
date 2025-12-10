import logging
import os

from openprocurement.api.migrations.base import BaseMigration, migrate
from openprocurement.tender.open.constants import ABOVE_THRESHOLD

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def has_value_restriction_populator(tender):
    pmt = tender.get("procurementMethodType")
    if pmt == ABOVE_THRESHOLD:
        return False
    return True


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with hasValueRestriction field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {
            "config.hasValueRestriction": {"$exists": False},
        },
        {"config": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            if tender.get("config", {}).get("hasValueRestriction") is None:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {"$set": {"config.hasValueRestriction": has_value_restriction_populator(tender)}},
                )
                count += 1
                if count % log_every == 0:
                    logger.info(f"Updating tenders with hasValueRestriction field: updated {count} tenders")
    finally:
        cursor.close()

    logger.info(f"Updating tenders with hasValueRestriction field finished: updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)
