# pylint: disable=wrong-import-position
from openprocurement.api.migrations.base import MigrationArgumentParser

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os
from time import sleep

from pyramid.paster import bootstrap

from openprocurement.api.utils import get_now

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def run(env):
    base_path = os.path.dirname(os.path.abspath(__file__))

    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    frameworks_collection = env["registry"].mongodb.frameworks.collection

    logger.info("Updating frameworks")

    count = 0

    cursor = frameworks_collection.find(
        {
            "status": "active",
            "enquiryPeriod.startDate": {
                "$exists": True,
            },
            "qualificationPeriod.startDate": {
                "$exists": True,
                "$ne": "enquiryPeriod.startDate",
            },
            "frameworkType": "electronicCatalogue",
        },
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for framework in cursor:
            now = get_now()

            logger.info(f"Updating framework {framework['_id']}: {now}")
            frameworks_collection.find_one_and_update(
                {"_id": framework["_id"], "_rev": framework["_rev"]},
                [
                    {
                        "$set": {
                            "qualificationPeriod.startDate": framework['enquiryPeriod']['startDate'],
                            "dateModified": now.isoformat(),
                            "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                        },
                    },
                ],
            )

            count += 1

            sleep(0.000001)
    finally:
        cursor.close()

    logger.info(f"Updated {count} frameworks")

    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env)
