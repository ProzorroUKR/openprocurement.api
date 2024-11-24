# pylint: disable=wrong-import-position

"""Migration for hasValueEstimation config parameter.

Add value estimation parameter to all existed tenders.
"""

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os

from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.tender.esco.constants import ESCO

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def has_value_estimation_populator(tender):
    """Populate tender with hasValueEstimation config parameter.

    :param tender: Tender instance
    :return: False if value is ESCO, True otherwise
    """
    pmt = tender.get("procurementMethodType")
    if pmt == ESCO:
        return False
    return True


def run(env, args):
    """Run the migration.

    :param env: WSGI environment
    :param args: command line arguments
    :return: None
    """
    migration_name = os.path.basename(__file__).split(".")[0]
    logger.info("Starting migration: %s", migration_name)
    logger.info("Updating tenders with hasValueEstimation field")
    log_every = 100000
    count = 0

    collection = env["registry"].mongodb.tenders.collection
    cursor = collection.find(
        {
            "config.hasValueEstimation": {"$exists": False},
        },
        {"config": 1, "procurementMethodType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)

    try:
        for tender in cursor:
            if tender.get("config", {}).get("hasValueEstimation") is None:
                collection.update_one(
                    {"_id": tender["_id"]},
                    {"$set": {"config.hasValueEstimation": has_value_estimation_populator(tender)}},
                )
                count += 1
                if count % log_every == 0:
                    logger.info("Updating tenders with hasValueEstimation field: updated %s tenders", count)
    finally:
        cursor.close()

    logger.info(f"Updating tenders with hasValueEstimation field finished: updated {count} tenders")
    logger.info(f"Successful migration: {migration_name}")


if __name__ == '__main__':
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
