from gevent import monkey

if __name__ == "__main__":
    monkey.patch_all(thread=False, select=False)

import os
import argparse
import logging

from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.competitivedialogue.constants import STAGE_2_UA_TYPE, CD_EU_TYPE
from openprocurement.tender.limited.constants import (
    REPORTING,
    NEGOTIATION,
    NEGOTIATION_QUICK,
)
from openprocurement.tender.open.constants import COMPETITIVE_ORDERING
from openprocurement.tender.pricequotation.constants import PQ

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def tender_complaints_populator(tender):
    pmt = tender.get("procurementMethodType")
    if pmt in (
        BELOW_THRESHOLD,
        COMPETITIVE_ORDERING,
        REPORTING,
        NEGOTIATION,
        NEGOTIATION_QUICK,
        PQ,
        CFA_SELECTION,
    ):
        return False
    return True


def award_complaints_populator(tender):
    pmt = tender.get("procurementMethodType")
    if pmt in (
        BELOW_THRESHOLD,
        COMPETITIVE_ORDERING,
        REPORTING,
        PQ,
        CFA_SELECTION,
        CD_EU_TYPE,
        STAGE_2_UA_TYPE,
    ):
        return False
    return True


def cancellation_complaints_populator(tender):
    pmt = tender.get("procurementMethodType")
    if pmt in (
        BELOW_THRESHOLD,
        COMPETITIVE_ORDERING,
        REPORTING,
        PQ,
        CFA_SELECTION,
    ):
        return False
    return True


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with tenderComplaints, awardComplaints, cancellationComplaints field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.tenderComplaints": {"$exists": False}},
        {"config": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            if tender.get("config", {}).get("tenderComplaints") is None:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {"$set": {
                        "config.tenderComplaints": tender_complaints_populator(tender),
                        "config.awardComplaints": award_complaints_populator(tender),
                        "config.cancellationComplaints": cancellation_complaints_populator(tender),
                    }}
                )
                count += 1
                if count % log_every == 0:
                    logger.info(
                        f"Updating tenders with complaints configurations: updated {count} tenders"
                    )
    finally:
        cursor.close()

    logger.info(
        f"Updating tenders with complaints configurations: updated {count} tenders"
    )

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
            "Limits the number of documents returned in one batch. Each batch "
            "requires a round trip to the server."
        )
    )
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
