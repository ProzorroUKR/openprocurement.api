# pylint: disable=wrong-import-position
from openprocurement.api.migrations.base import MigrationArgumentParser

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os

from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def restricted_populator(agreement):
    return False


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.agreements.collection

    logger.info("Updating agreements with restricted field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.restricted": {"$exists": False}},
        {"config": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for agreement in cursor:
            if agreement.get("config", {}).get("restricted") is None:
                try:
                    collection.update_one(
                        {"_id": agreement["_id"]}, {"$set": {"config.restricted": restricted_populator(agreement)}}
                    )
                    count += 1
                    if count % log_every == 0:
                        logger.info(f"Updating agreements with restricted field: updated {count} agreements")
                except OperationFailure as e:
                    logger.warning(f"Skip updating agreement {agreement['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(f"Updating agreements with restricted field finished: updated {count} agreements")

    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
