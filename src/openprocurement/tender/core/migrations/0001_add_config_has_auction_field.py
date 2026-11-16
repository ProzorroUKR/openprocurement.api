import logging
import os

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.migrations.base import BaseMigration, migrate

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def has_auction_populator(tender, ignore_submission_method_details=False):
    pmt = tender.get("procurementMethodType")

    if pmt == ProcurementMethodType.ABOVE_THRESHOLD and not ignore_submission_method_details:
        smd = tender.get("submissionMethodDetails") or ""
        if "quick(mode:no-auction)" in smd:
            return False
        else:
            return True

    if pmt in (
        ProcurementMethodType.REPORTING,
        ProcurementMethodType.NEGOTIATION,
        ProcurementMethodType.NEGOTIATION_QUICK,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
        ProcurementMethodType.PRICE_QUOTATION,
    ):
        return False
    return True


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with hasAuction field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.hasAuction": {"$exists": False}},
        {"config": 1, "procurementMethodType": 1, "submissionMethodDetails": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            if tender.get("config", {}).get("hasAuction") is None:
                collection.update_one(
                    {"_id": tender["_id"]}, {"$set": {"config.hasAuction": has_auction_populator(tender)}}
                )
                count += 1
                if count % log_every == 0:
                    logger.info("Updating tenders with hasAuction field: updated %s tenders", count)
    finally:
        cursor.close()

    logger.info("Updating tenders with hasAuction field finished: updated %s tenders", count)

    logger.info("Successful migration: %s", migration_name)


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)
