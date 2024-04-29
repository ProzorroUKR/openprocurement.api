# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import argparse
import logging
import os

from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR
from openprocurement.tender.cfaua.constants import CFA_UA
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE,
    CD_UA_TYPE,
    STAGE_2_EU_TYPE,
)
from openprocurement.tender.esco.constants import ESCO
from openprocurement.tender.openeu.constants import ABOVE_THRESHOLD_EU

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def has_qualification_complaints_populator(tender):
    pmt = tender.get("procurementMethodType")

    if pmt in (
        ABOVE_THRESHOLD_EU,
        CD_UA_TYPE,
        CD_EU_TYPE,
        STAGE_2_EU_TYPE,
        ESCO,
        CFA_UA,
    ):
        return True
    return False


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with hasQualificationComplaints field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.hasQualificationComplaints": {"$exists": False}},
        {"config": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            if tender.get("config", {}).get("hasQualificationComplaints") is None:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {"$set": {"config.hasQualificationComplaints": has_qualification_complaints_populator(tender)}},
                )
                count += 1
                if count % log_every == 0:
                    logger.info("Updating tenders with hasQualificationComplaints field: updated %s tenders", count)
    finally:
        cursor.close()

    logger.info("Updating tenders with hasQualificationComplaints field finished: updated %s tenders", count)

    logger.info("Successful migration: %s", migration_name)


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
