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


def clarification_until_duration_populator(framework):
    framework_type = framework.get("frameworkType")
    if framework_type in ("electronicCatalogue", "dynamicPurchasingSystem"):
        return 3


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.frameworks.collection

    logger.info("Updating frameworks with clarificationUntilDuration field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.clarificationUntilDuration": {"$exists": False}},
        {"config": 1, "frameworkType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for framework in cursor:
            if framework.get("config", {}).get("clarificationUntilDuration") is None:
                try:
                    collection.update_one(
                        {"_id": framework["_id"]},
                        {
                            "$set": {
                                "config.clarificationUntilDuration": clarification_until_duration_populator(framework)
                            }
                        },
                    )
                    count += 1
                    if count % log_every == 0:
                        logger.info(
                            f"Updating frameworks with clarificationUntilDuration field: updated {count} frameworks"
                        )
                except OperationFailure as e:
                    logger.warning(f"Skip updating framework {framework['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(f"Updating frameworks with clarificationUntilDuration field finished: updated {count} frameworks")

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
