import logging
import os

from pymongo.errors import OperationFailure

from openprocurement.api.migrations.base import BaseMigration, migrate
from openprocurement.api.utils import get_now
from openprocurement.framework.dps.constants import DPS_TYPE

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def get_kind(revisions):
    for rev in revisions:
        for change in rev.get("changes", ""):
            if change.get("op", "") == "replace" and change.get("path", "") == "/procuringEntity/kind":
                return change.get("value", "")


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.frameworks.collection

    logger.info("Updating frameworks replaced procuringEntity.kind")

    log_every = 100000
    count = 0
    framework_ids = []

    cursor = collection.find(
        {"frameworkType": DPS_TYPE},
        {"procuringEntity": 1, "revisions": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for framework in cursor:
            if kind := get_kind(framework["revisions"]):
                try:
                    collection.update_one(
                        {"_id": framework["_id"]},
                        {"$set": {"procuringEntity.kind": kind, "public_modified": get_now().timestamp()}},
                    )
                    count += 1
                    framework_ids.append(framework["_id"])
                    if count % log_every == 0:
                        logger.info(f"Updating frameworks with replaced kind: updated {count} frameworks")
                except OperationFailure as e:
                    logger.warning(f"Skip updating framework {framework['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(f"Updating frameworks with replaced procuringEntity.kind finished: updated {count} frameworks")
    logger.info(f"List of updated frameworks: {framework_ids}")

    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)
