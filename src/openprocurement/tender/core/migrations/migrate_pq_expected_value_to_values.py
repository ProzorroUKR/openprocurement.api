from copy import deepcopy

from gevent import monkey

from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.constants import PQ

if __name__ == "__main__":
    monkey.patch_all(thread=False, select=False)

import argparse
import logging
import os

from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def update_criteria(criteria: list) -> list:
    if not criteria:
        return []
    updated_criteria = []
    updated = False

    for criterion in criteria:
        updated_criterion = deepcopy(criterion)
        for req_group in updated_criterion.get("requirementGroups", []):
            for requirement in req_group.get("requirements", []):
                if "expectedValue" in requirement:
                    requirement["expectedValues"] = [requirement["expectedValue"]]
                    del requirement["expectedValue"]
                    updated = True
        updated_criteria.append(updated_criterion)
    return updated_criteria if updated else []


def update_requirement_responses(req_responses: list) -> list:
    if not req_responses:
        return []
    updated = False
    updated_req_responses = []

    for req_response in req_responses:
        updated_response = deepcopy(req_response)
        if "value" in updated_response:
            updated_response["values"] = [updated_response["value"]]
            del updated_response["value"]
            updated = True
        updated_req_responses.append(updated_response)
    return updated_req_responses if updated else []


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Migrating PQ tenders from expected value to values field")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {
            "procurementMethodType": PQ,
            "criteria": {"$exists": True},
        },
        {"criteria": 1, "bids": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            now = get_now()
            set_data = {
                "dateModified": now.isoformat(),  # TODO: discuss it
                "public_modified": now.timestamp(),
            }
            update_tender = False
            if updated_criteria := update_criteria(tender["criteria"]):
                set_data["criteria"] = updated_criteria
                update_tender = True

            if tender.get("bids"):
                updated_bids = []
                update_bids = False
                for bid in tender["bids"]:
                    if updated_rr := update_requirement_responses(bid["requirementResponses"]):
                        bid["requirementResponses"] = updated_rr
                        update_tender = update_bids = True
                    updated_bids.append(bid)
                if update_bids:
                    set_data["bids"] = updated_bids

            if update_tender:
                collection.update_one({"_id": tender["_id"]}, {"$set": set_data})
                count += 1
            if count and count % log_every == 0:
                logger.info(f"Updating PQ tenders from expected value to values field: updated {count} tenders")
    finally:
        cursor.close()

    logger.info(f"Updating PQ tenders from expected value to values field finished: updated {count} tenders")

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
