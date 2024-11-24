# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os

from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.pricequotation.constants import PQ

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def has_auction_populator(tender, ignore_submission_method_details=False):
    pmt = tender.get("procurementMethodType")

    if pmt == ABOVE_THRESHOLD and not ignore_submission_method_details:
        smd = tender.get("submissionMethodDetails") or ""
        if "quick(mode:no-auction)" in smd:
            return False
        else:
            return True

    if pmt in (
        REPORTING,
        NEGOTIATION,
        NEGOTIATION_QUICK,
        CD_UA_TYPE,
        CD_EU_TYPE,
        PQ,
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


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
