import logging
import os

from pymongo.errors import OperationFailure

from openprocurement.api.migrations.base import BaseMigration, migrate

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def qualification_complain_duration_populator(framework):
    framework_type = framework.get("frameworkType")
    if framework_type in ("electronicCatalogue", "dynamicPurchasingSystem"):
        return 0


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.frameworks.collection

    logger.info("Updating frameworks with qualificationComplainDuration field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {"config.qualificationComplainDuration": {"$exists": False}},
        {"config": 1, "frameworkType": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for framework in cursor:
            if framework.get("config", {}).get("qualificationComplainDuration") is None:
                try:
                    collection.update_one(
                        {"_id": framework["_id"]},
                        {
                            "$set": {
                                "config.qualificationComplainDuration": qualification_complain_duration_populator(
                                    framework
                                )
                            }
                        },
                    )
                    count += 1
                    if count % log_every == 0:
                        logger.info(
                            f"Updating frameworks with qualificationComplainDuration field: updated {count} frameworks"
                        )
                except OperationFailure as e:
                    logger.warning(f"Skip updating framework {framework['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(f"Updating frameworks with qualificationComplainDuration field finished: updated {count} frameworks")

    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)
