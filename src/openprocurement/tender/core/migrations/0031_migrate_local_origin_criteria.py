# pylint: disable=wrong-import-position
if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os
from bson import Timestamp

from pymongo import UpdateOne
from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.constants import COUNTRIES_MAP
from openprocurement.api.database import get_public_ts
from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.api.utils import get_now
from openprocurement.tender.core.constants import CRITERION_LOCALIZATION
from openprocurement.tender.core.procedure.models.criterion import DataSchema

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def bulk_update(bulk, collection):
    bulk_size = len(bulk)
    try:
        collection.bulk_write(bulk)
        return bulk_size
    except OperationFailure as e:
        logger.warning(f"Skip updating {bulk_size} tenders. Details: {e}")
        return 0


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Migrating tenders localization criteria")

    log_every = 100000
    bulk = []
    count = 0
    bulk_max_size = 500

    cursor = collection.find(
        {"criteria": {"$exists": True}},
        {"criteria": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            is_updated = False
            for criterion in tender["criteria"]:
                if criterion.get("classification", {}).get("id") == CRITERION_LOCALIZATION:
                    for rg in criterion.get("requirementGroups", []):
                        for req in rg.get("requirements", []):
                            if req.get("expectedValues") is not None and not set(req["expectedValues"]) - set(
                                COUNTRIES_MAP.keys()
                            ):
                                req["dataSchema"] = DataSchema.ISO_3166.value
                                is_updated = True
            if is_updated:
                bulk.append(
                    UpdateOne(
                        {"_id": tender["_id"]},
                        {
                            "$set": {
                                "criteria": tender["criteria"],
                                "public_modified": get_now().timestamp(),
                                "public_ts": Timestamp(int(get_now().timestamp()), 0),
                            }
                        },
                    )
                )

                if bulk and len(bulk) % bulk_max_size == 0:
                    count += bulk_update(bulk, collection)
                    bulk = []

                    if count % log_every == 0:
                        logger.info(f"Updated tender's localization criteria: {count} updated")
    finally:
        cursor.close()

    if bulk:
        count += bulk_update(bulk, collection)

    logger.info(f"Updating tenders localization criteria: updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
