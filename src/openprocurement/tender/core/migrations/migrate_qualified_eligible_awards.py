# pylint: disable=wrong-import-position
from time import sleep

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import argparse
import logging
import os

from pymongo import UpdateOne
from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
)
from openprocurement.tender.pricequotation.constants import PQ

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def get_previous_status(revisions, award_idx):
    for rev in revisions:
        for change in rev.get("changes", ""):
            if change.get("op", "") == "replace" and change.get("path", "") == f"/awards/{award_idx}/status":
                if change.get("value", "") in ("active", "unsuccessful"):
                    return change["value"]


def bulk_update(bulk, collection):
    bulk_size = len(bulk)
    try:
        collection.bulk_write(bulk)
        return bulk_size
    except OperationFailure as e:
        logger.warning(f"Skip updating {bulk_size} tenders. Details: {e}")
        return 0


def tender_with_eligible_awards(pmt):
    return pmt not in (BELOW_THRESHOLD, REPORTING, NEGOTIATION, NEGOTIATION_QUICK, CFA_SELECTION, PQ)


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tender's awards with qualified/eligible")

    log_every = 100000

    cursor = collection.find(
        {"awards": {"$exists": 1}},
        {"awards": 1, "revisions": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    bulk = []
    count = 0
    bulk_max_size = 500
    try:
        for tender in cursor:
            pmt = tender.get("procurementMethodType")
            for idx, award in enumerate(tender.get("awards", [])):
                status = award.get("status")
                if status == "cancelled":
                    status = get_previous_status(tender["revisions"], idx)
                if status == "active":
                    award["qualified"] = True
                    if tender_with_eligible_awards(pmt):
                        award["eligible"] = True
                elif status == "unsuccessful":
                    award["qualified"] = False
                    if tender_with_eligible_awards(pmt):
                        award["eligible"] = False

            bulk.append(UpdateOne({"_id": tender["_id"]}, {"$set": {"awards": tender["awards"]}}))

            if bulk and len(bulk) % bulk_max_size == 0:
                count += bulk_update(bulk, collection)
                bulk = []

                if count % log_every == 0:
                    logger.info(f"Updating tender's awards with qualified/eligible: {count} updated")

        sleep(0.000001)
    finally:
        cursor.close()

    if bulk:
        count += bulk_update(bulk, collection)

    logger.info(f"Updated {count} tenders")
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
        help="Limits the number of documents returned in one batch. Each batch requires a round trip to the server.",
    )
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
