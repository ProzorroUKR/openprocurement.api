# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os

from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def qualification_complain_duration_populator(qualification):
    return 0


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.qualifications.collection

    logger.info("Updating qualifications with qualificationComplainDuration field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.qualificationComplainDuration": {"$exists": False}},
        {"config": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for qualification in cursor:
            if qualification.get("config", {}).get("qualificationComplainDuration") is None:
                try:
                    collection.update_one(
                        {"_id": qualification["_id"]},
                        {
                            "$set": {
                                "config.qualificationComplainDuration": qualification_complain_duration_populator(
                                    qualification
                                )
                            }
                        },
                    )
                    count += 1
                    if count % log_every == 0:
                        logger.info(
                            f"Updating qualifications with qualificationComplainDuration field: updated {count} qualifications"
                        )
                except OperationFailure as e:
                    logger.warning(f"Skip updating qualification {qualification['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(
        f"Updating qualifications with qualificationComplainDuration field finished: updated {count} qualifications."
    )

    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
