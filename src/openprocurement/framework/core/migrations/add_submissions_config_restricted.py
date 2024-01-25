from gevent import monkey
from pymongo.errors import OperationFailure

if __name__ == "__main__":
    monkey.patch_all(thread=False, select=False)

import os
import argparse
import logging

from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def restricted_populator(submission):
    return False


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.submissions.collection

    logger.info("Updating submissions with restricted field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.restricted": {"$exists": False}},
        {"config": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for submission in cursor:
            if submission.get("config", {}).get("restricted") is None:
                try:
                    collection.update_one(
                        {"_id": submission["_id"]},
                        {"$set": {"config.restricted": restricted_populator(submission)}}
                    )
                    count += 1
                    if count % log_every == 0:
                        logger.info(f"Updating submissions with restricted field: updated {count} submissions")
                except OperationFailure as e:
                    logger.warning(f"Skip updating submission {submission['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(f"Updating submissions with restricted field finished: updated {count} submissions")

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
