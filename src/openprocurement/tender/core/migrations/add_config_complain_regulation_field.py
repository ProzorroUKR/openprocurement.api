# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import argparse
import logging
import os

from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD, COMPETITIVE_ORDERING
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        default=os.path.join(BASE_DIR, "etc/service.ini"),
        help="Path to service.ini file",
    )
    parser.add_argument(
        "-b",
        type=int,
        default=1000,
        help=(
            "Limits the number of documents returned in one batch. Each batch " "requires a round trip to the server."
        ),
    )
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
