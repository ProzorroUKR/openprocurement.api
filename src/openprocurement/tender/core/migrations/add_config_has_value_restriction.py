from gevent import monkey

if __name__ == "__main__":
    monkey.patch_all(thread=False, select=False)

import argparse
import logging
import os

from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR
from openprocurement.tender.open.constants import ABOVE_THRESHOLD

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def has_value_restriction_populator(tender):
    pmt = tender.get("procurementMethodType")
    if pmt == ABOVE_THRESHOLD:
        return False
    return True


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating tenders with hasValueRestriction field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {
            "config.hasValueRestriction": {"$exists": False},
        },
        {"config": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            if tender.get("config", {}).get("hasValueRestriction") is None:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {"$set": {"config.hasValueRestriction": has_value_restriction_populator(tender)}},
                )
                count += 1
                if count % log_every == 0:
                    logger.info(f"Updating tenders with hasValueRestriction field: updated {count} tenders")
    finally:
        cursor.close()

    logger.info(f"Updating tenders with hasValueRestriction field finished: updated {count} tenders")

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
