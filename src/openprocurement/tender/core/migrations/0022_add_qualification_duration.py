import logging
import os

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.migrations.base import BaseMigration, migrate

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def qualification_duration_populator(tender):
    pmt = tender.get("procurementMethodType")
    if pmt in [
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
        ProcurementMethodType.ESCO,
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
    ]:
        return 20
    else:
        return 0


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with qualificationDuration field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.qualificationDuration": {"$exists": False}},
        {"config": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            if tender.get("config", {}).get("qualificationDuration") is None:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {
                        "$set": {"config.qualificationDuration": qualification_duration_populator(tender)},
                    },
                )
                count += 1
                if count % log_every == 0:
                    logger.info(f"Updating tenders with qualificationDuration field: updated {count} tenders")
    finally:
        cursor.close()

    logger.info(f"Updating tenders with qualificationDuration field finished: updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)
