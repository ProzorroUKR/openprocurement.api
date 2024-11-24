# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all()

import logging
import os

from pymongo import UpdateOne
from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def bulk_update(bulk, collection):
    bulk_size = len(bulk)
    try:
        collection.bulk_write(bulk)
        return bulk_size
    except OperationFailure as e:
        logger.warning(f"Skip updating {bulk_size} contracts Details: {e}")
        return 0


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.contracts.collection

    logger.info("Updating contracts is_test field")

    cursor = collection.find(
        {"mode": "test", "$or": [{"is_test": False}, {"is_test": {"$exists": False}}]},
        {"is_test": True},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)

    bulk = []
    bulk_max_size = 500
    count = 0
    log_every = 100000

    try:
        for contract in cursor:
            bulk.append(UpdateOne({"_id": contract["_id"]}, {"$set": {"is_test": True}}))
            if bulk and len(bulk) % bulk_max_size == 0:
                count += bulk_update(bulk, collection)
                bulk = []

                if count % log_every == 0:
                    logger.info(f"Updating contracts is_test: {count} updated")

        if bulk:
            count += bulk_update(bulk, collection)
    finally:
        cursor.close()

    logger.info(f"Updating contracts is_test: updated {count} contracts")
    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
