import logging
import os
import traceback

from openprocurement.api.migrations.base import BaseMigration, migrate

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def update_requirement_responses(rrs: list):
    if not rrs:
        return False

    changed = False
    fields_to_delete = (
        "title",
        "title_en",
        "title_ru",
        "description",
        "description_en",
        "description_ru",
        "requirement.title",
    )
    for rr in rrs:
        for field in fields_to_delete:
            if field == "requirement.title":
                was_deleted = rr.get("requirement", {}).pop("title", None)

            else:
                was_deleted = rr.pop(field, None)

            if was_deleted:
                changed = True
    return changed


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Migrating Tenders requirement responses")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {
            "criteria": {"$exists": True},
        },
        {"bids": 1, "awards": 1, "qualifications": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            updated_data = {}
            try:
                for obj_name in ("bids", "awards", "qualifications"):
                    is_updated = False
                    for i in tender.get(obj_name, ""):
                        if update_requirement_responses(i.get("requirementResponses", "")):
                            is_updated = True

                    if is_updated:
                        updated_data[obj_name] = tender[obj_name]

                if updated_data:
                    collection.update_one(
                        {"_id": tender["_id"]},
                        {"$set": updated_data},
                    )
                    count += 1

                if count and count % log_every == 0:
                    logger.info(
                        f"Updating tenders requirementResponses(bids, awards, qualifications): "
                        f"updated {count} tenders"
                    )
            except Exception as e:
                logger.info(f"ERROR: Tender with id {tender['_id']}. Caught {type(e).__name__}.")
                traceback.print_exc()
                break
    finally:
        cursor.close()

    logger.info(f"Updating tenders requirementResponses(bids, awards, qualifications) updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)
