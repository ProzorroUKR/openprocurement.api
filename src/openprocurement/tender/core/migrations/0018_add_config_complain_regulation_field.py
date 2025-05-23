import logging
import os

from openprocurement.api.migrations.base import BaseMigration, migrate
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.openuadefense.constants import ABOVE_THRESHOLD_UA_DEFENSE
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.simpledefense.constants import SIMPLE_DEFENSE

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def tender_complain_regulation_populator(tender):
    pmt = tender.get("procurementMethodType")
    _map = {
        ABOVE_THRESHOLD: 3,
        BELOW_THRESHOLD: 0,
        SIMPLE_DEFENSE: 2,
        CFA_SELECTION: 0,
        PQ: 0,
        ABOVE_THRESHOLD_UA_DEFENSE: 2,
        REPORTING: 0,
        NEGOTIATION: 0,
        NEGOTIATION_QUICK: 0,
        COMPETITIVE_ORDERING: 0,
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
