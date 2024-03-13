# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import argparse
import logging
import os

from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def restricted_populator(contract):
    return False


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.contracts.collection

    logger.info("Updating contracts with restricted field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.restricted": {"$exists": False}},
        {"config": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for contract in cursor:
            if contract.get("config", {}).get("restricted") is None:
                try:
                    collection.update_one(
                        {"_id": contract["_id"]}, {"$set": {"config.restricted": restricted_populator(contract)}}
                    )
                    count += 1
                    if count % log_every == 0:
                        logger.info(f"Updating contracts with restricted field: updated {count} contracts")
                except OperationFailure as e:
                    logger.warning(f"Skip updating contract {contract['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(f"Updating contracts with restricted field finished: updated {count} contracts")

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
