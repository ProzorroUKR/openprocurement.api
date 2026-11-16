import logging
import os

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.migrations.base import BaseMigration, migrate

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def tender_complain_regulation_populator(tender):
    pmt = tender.get("procurementMethodType")
    _map = {
        ProcurementMethodType.ABOVE_THRESHOLD: 3,
        ProcurementMethodType.BELOW_THRESHOLD: 0,
        ProcurementMethodType.SIMPLE_DEFENSE: 2,
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA: 0,
        ProcurementMethodType.PRICE_QUOTATION: 0,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: 2,
        ProcurementMethodType.REPORTING: 0,
        ProcurementMethodType.NEGOTIATION: 0,
        ProcurementMethodType.NEGOTIATION_QUICK: 0,
        ProcurementMethodType.COMPETITIVE_ORDERING: 0,
    }
    return _map.get(pmt, 4)


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with tenderComplainRegulation field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.tenderComplainRegulation": {"$exists": False}},
        {"config": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            if tender.get("config", {}).get("tenderComplainRegulation") is None:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {
                        "$set": {"config.tenderComplainRegulation": tender_complain_regulation_populator(tender)},
                        # "$unset": {"complaintPeriod": ""},  # WTF was this?
                    },
                )
                count += 1
                if count % log_every == 0:
                    logger.info(f"Updating tenders with tenderComplainRegulation field: updated {count} tenders")
    finally:
        cursor.close()

    logger.info(f"Updating tenders with tenderComplainRegulation field finished: updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)
