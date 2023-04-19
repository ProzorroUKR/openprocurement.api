#!/usr/bin/env python
from gevent import monkey

if __name__ == "__main__":
    monkey.patch_all(thread=False, select=False)

import os
import argparse
import logging

from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR
from openprocurement.tender.competitivedialogue.constants import (
    CD_UA_TYPE,
    CD_EU_TYPE,
)
from openprocurement.tender.limited.constants import (
    REPORTING,
    NEGOTIATION,
    NEGOTIATION_QUICK,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.pricequotation.constants import PQ

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def has_auction_populator(tender):
    pmt = tender.get("procurementMethodType")

    if pmt == ABOVE_THRESHOLD:
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

def run(env):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with hasAuction field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.hasAuction": {"$exists": False}},
        {"config": 1, "procurementMethodType": 1, "submissionMethodDetails": 1},
    )
    for tender in cursor:
        if tender.get("config", {}).get("hasAuction") is None:
            collection.update_one(
                {"_id": tender["_id"]},
                {"$set": {"config.hasAuction": has_auction_populator(tender)}}
            )
            count += 1
            if count % log_every == 0:
                logger.info("Updating tenders with hasAuction field: updated %s tenders", count)

    logger.info("Updating tenders with hasAuction field finished: updated %s tenders", count)

    logger.info("Successful migration: %s", migration_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", help="Path to service.ini file")
    args = parser.parse_args()
    path_to_ini_file = args.p if args.p else os.path.join(BASE_DIR, "etc/service.ini")
    with bootstrap(path_to_ini_file) as env:
        run(env)
