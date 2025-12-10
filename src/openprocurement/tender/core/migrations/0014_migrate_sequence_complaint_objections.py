import logging
import os
from copy import deepcopy
from datetime import datetime
from time import sleep

from pymongo import UpdateOne
from pymongo.errors import OperationFailure

from openprocurement.api.migrations.base import BaseMigration, migrate

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Release 2.6.230 (release with objections)
DATE = datetime(year=2023, month=11, day=8)


def add_sequence_numbers(complaints):
    modified = False
    for complaint in complaints:
        if objections := complaint.get("objections", []):
            for number, objection in enumerate(objections, start=1):
                if objection.get("sequenceNumber") != number:
                    objection["sequenceNumber"] = number
                    modified = True
                # migrate old criterion from article_16 dictionary
                if objection["classification"]["id"] == (
                    "CRITERION.SELECTION.ECONOMIC_FINANCIAL_STANDING.TURNOVER.GENERAL_YEARLY"
                ):
                    objection["classification"]["id"] = "CRITERION.SELECTION.ECONOMIC_FINANCIAL_STANDING"
                    modified = True
    return modified


def numerate_objections(tender):
    updated_fields = {}

    # Process complaints in the main tender object
    if "complaints" in tender:
        updated_complaints = deepcopy(tender["complaints"])
        if add_sequence_numbers(updated_complaints):
            updated_fields["complaints"] = updated_complaints

    # Process complaints in other tender objects
    for objs in ("awards", "qualifications", "cancellations"):
        if objs in tender:
            updated_objs = deepcopy(tender[objs])
            objs_modified = False
            for obj in updated_objs:
                if add_sequence_numbers(obj.get("complaints", [])):
                    objs_modified = True
            if objs_modified:
                updated_fields[objs] = updated_objs

    return updated_fields


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

    logger.info("Updating tender's complaints objections with sequenceNumber")

    log_every = 100000

    cursor = collection.find(
        {"public_modified": {"$gte": DATE.timestamp()}},
        {"complaints": 1, "awards": 1, "cancellations": 1, "qualifications": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    bulk = []
    count = 0
    bulk_max_size = 500
    try:
        for tender in cursor:
            updated_fields = numerate_objections(tender)

            if updated_fields:
                bulk.append(UpdateOne({"_id": tender["_id"]}, {"$set": updated_fields}))

            if bulk and len(bulk) % bulk_max_size == 0:
                count += bulk_update(bulk, collection)
                bulk = []

                if count % log_every == 0:
                    logger.info(f"Updating tender's complaints objections sequenceNumber: {count} updated")

        sleep(0.000001)
    finally:
        cursor.close()

    if bulk:
        count += bulk_update(bulk, collection)

    logger.info(f"Updated {count} tenders")
    logger.info(f"Successful migration: {migration_name}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)
