# pylint: disable=wrong-import-position
import traceback

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import argparse
import logging
import os
from copy import deepcopy

from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR
from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.constants import PQ

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def convert_expected_value_to_string(requirement):
    requirement["dataType"] = "string"
    requirement["expectedValues"] = [str(requirement.pop("expectedValue"))]
    requirement["expectedMinItems"] = 1


def normalize_expected_values(requirement):
    requirement["dataType"] = "string"
    requirement["expectedValues"] = [str(value) for value in requirement["expectedValues"]]
    requirement["expectedMinItems"] = 1


def convert_field_to_float(requirement, field_name):
    if isinstance(requirement[field_name], (float, int)):
        requirement[field_name] = float(requirement[field_name])
        requirement["dataType"] = "number"
        return True
    return False


def pop_min_max_values(requirement):
    requirement.pop("maxValue", None)
    requirement.pop("minValue", None)


def update_bids_responses(bids, requirement, obj_type):
    if bids:
        updated_bids = []
        for bid_data in bids:
            req_resp = []
            updated = False
            bid = deepcopy(bid_data)
            for resp in bid.get("requirementResponses", []):
                try:
                    if resp["requirement"] == requirement["title"]:
                        if resp.get("value") is not None:
                            if not isinstance(resp["value"], obj_type):
                                resp["value"] = obj_type(resp["value"])
                                updated = True
                        elif resp.get("values") is not None:
                            for value in resp["values"]:
                                if not isinstance(value, obj_type):
                                    break
                            else:
                                continue
                            resp["values"] = [obj_type(val) for val in resp["values"]]
                            updated = True
                except ValueError as e:
                    # delete such response
                    updated = True
                else:
                    req_resp.append(resp)
            if updated:
                bid["requirementResponses"] = req_resp
            updated_bids.append(bid)
        return updated_bids
    return bids


def get_responses_from_bids(bids, requirement):
    responses = set()
    for bid in bids:
        for resp in bid.get("requirementResponses", []):
            if resp["requirement"] == requirement["title"]:
                if resp.get("value") is not None:
                    responses.add(resp["value"])
                elif resp.get("values") is not None:
                    responses.update(resp["values"])
    return responses


def get_min_value_from_responses(requirement, bids, obj_type):
    responses = get_responses_from_bids(bids, requirement)
    if responses:
        responses = [obj_type(resp) for resp in responses]
        requirement["minValue"] = min(responses)
    else:
        requirement["minValue"] = 0


def update_criteria_and_responses_integer(requirement, bids):
    if "expectedValues" in requirement:
        normalize_expected_values(requirement)
        bids = update_bids_responses(bids, requirement, str)
    elif "minValue" in requirement or "maxValue" in requirement or "expectedValue" in requirement:
        for field_name in ("minValue", "maxValue", "expectedValue"):
            if field_name in requirement:
                if isinstance(requirement[field_name], float):
                    requirement["dataType"] = "number"
                    bids = update_bids_responses(bids, requirement, float)
                elif field_name == "expectedValue" and isinstance(requirement["expectedValue"], (bool, str)):
                    convert_expected_value_to_string(requirement)
                    bids = update_bids_responses(bids, requirement, str)
    else:
        get_min_value_from_responses(requirement, bids, int)
    return bids


def update_criteria_and_responses_number(requirement, bids):
    if "expectedValues" in requirement:
        normalize_expected_values(requirement)
        bids = update_bids_responses(bids, requirement, str)
    elif "minValue" in requirement or "maxValue" in requirement or "expectedValue" in requirement:
        for field_name in ("minValue", "maxValue", "expectedValue"):
            if field_name in requirement:
                if field_name == "expectedValue" and isinstance(requirement["expectedValue"], (bool, str)):
                    convert_expected_value_to_string(requirement)
                    bids = update_bids_responses(bids, requirement, str)
                elif convert_field_to_float(requirement, field_name):
                    bids = update_bids_responses(bids, requirement, float)
    else:
        get_min_value_from_responses(requirement, bids, float)
    return bids


def update_criteria_and_responses_string(requirement, bids):
    if "expectedValues" in requirement:
        normalize_expected_values(requirement)
    elif "expectedValue" in requirement:
        convert_expected_value_to_string(requirement)
    # maxValue + minValue одночасно
    elif "minValue" in requirement and "maxValue" in requirement:
        responses = get_responses_from_bids(bids, requirement)
        if responses:
            requirement["expectedValues"] = [str(resp) for resp in responses]
        else:
            requirement["expectedValues"] = [str(requirement["minValue"]), str(requirement["maxValue"])]
        requirement["expectedMinItems"] = 1
        pop_min_max_values(requirement)
    elif "minValue" in requirement or "maxValue" in requirement:
        for field_name in ("minValue", "maxValue"):
            if field_name in requirement:
                responses = get_responses_from_bids(bids, requirement)
                if responses:
                    requirement["expectedValues"] = [str(resp) for resp in responses]
                else:
                    requirement["expectedValues"] = [str(requirement[field_name])]
                requirement["expectedMinItems"] = 1
                pop_min_max_values(requirement)
    else:
        responses = get_responses_from_bids(bids, requirement)
        if responses:
            requirement["expectedValues"] = [str(resp) for resp in responses]
            requirement["expectedMinItems"] = 1
        else:
            requirement["dataType"] = "boolean"
    bids = update_bids_responses(bids, requirement, str)
    return bids


def update_criteria_and_responses_boolean(requirement, bids):
    if "expectedValues" in requirement:
        if len(requirement["expectedValues"]) == 1:
            if isinstance(requirement["expectedValues"][0], bool):
                requirement["expectedValue"] = requirement["expectedValues"][0]
                for field_name in ("expectedValues", "expectedMinItems", "expectedMaxItems"):
                    requirement.pop(field_name, None)
                bids = update_bids_responses(bids, requirement, bool)
        elif set(requirement["expectedValues"]) == {True, False}:
            for field_name in ("expectedValues", "expectedMinItems", "expectedMaxItems"):
                requirement.pop(field_name, None)
            bids = update_bids_responses(bids, requirement, bool)
        # check whether expectedValues is left
        if requirement.get("expectedValues"):
            normalize_expected_values(requirement)
            bids = update_bids_responses(bids, requirement, str)
    elif "expectedValue" in requirement:
        convert_expected_value_to_string(requirement)
        bids = update_bids_responses(bids, requirement, str)
    return bids


def update_criteria(criteria: list, bids: list):
    if not criteria:
        return [], bids
    updated_criteria = []

    for criterion in criteria:
        updated_criterion = deepcopy(criterion)
        for req_group in updated_criterion.get("requirementGroups", []):
            for requirement in req_group.get("requirements", []):
                # Remove min/max values if expected values exist
                if ("expectedValue" in requirement or "expectedValues" in requirement) and (
                    "minValue" in requirement or "maxValue" in requirement
                ):
                    pop_min_max_values(requirement)
                # Handle different data types
                if requirement["dataType"] == "integer":
                    bids = update_criteria_and_responses_integer(requirement, bids)
                elif requirement["dataType"] == "number":
                    bids = update_criteria_and_responses_number(requirement, bids)
                elif requirement["dataType"] == "string":
                    bids = update_criteria_and_responses_string(requirement, bids)
                elif requirement["dataType"] == "boolean":
                    bids = update_criteria_and_responses_boolean(requirement, bids)

                # delete unit from string and boolean requirements
                if requirement["dataType"] in ("string", "boolean"):
                    requirement.pop("unit", None)
        updated_criteria.append(updated_criterion)
    return updated_criteria, bids


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Migrating PQ requirements")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {
            "status": {"$in": ["draft", "active.tendering"]},
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
                "dateModified": now.isoformat(),
                "public_modified": now.timestamp(),
            }
            try:
                updated_criteria, updated_bids = update_criteria(tender["criteria"], tender.get("bids", []))
                if updated_criteria:
                    set_data["criteria"] = updated_criteria
                if updated_bids:
                    set_data["bids"] = updated_bids
                if updated_criteria or updated_bids:
                    collection.update_one(
                        {"_id": tender["_id"]},
                        {"$set": set_data},
                    )
                    count += 1
                if count and count % log_every == 0:
                    logger.info(f"Updating PQ tenders requirements: updated {count} tenders")
            except Exception as e:
                logger.info(f"ERROR: Tender with id {tender['_id']}. Caught {type(e).__name__}.")
                traceback.print_exc()
                break
    finally:
        cursor.close()

    logger.info(f"Updating PQ tenders requirements finished: updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


def create_temporary_db(env):
    collection = env["registry"].mongodb.tenders.collection

    logger.info("Create temporary DB with PQ tenders")

    env["registry"].mongodb.pq_tenders.collection.insert_many(
        list(
            collection.find(
                {
                    "status": {"$in": ["draft", "active.tendering"]},
                    "procurementMethodType": PQ,
                    "criteria": {"$exists": True},
                },
                no_cursor_timeout=True,
            )
        )
    )
    logger.info("Temporary DB with PQ tenders successfully created")


def revert_tenders(env, args):
    pq_collection = env["registry"].mongodb.pq_tenders.collection
    collection = env["registry"].mongodb.tenders.collection

    logger.info("Reverting PQ requirements")
    cursor = pq_collection.find(
        {},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        for tender in cursor:
            collection.replace_one(
                {"_id": tender["_id"]},
                tender,
            )
    finally:
        cursor.close()

    logger.info("Successful revert!")


def flush_temporary_database(env):
    logger.info("Flush temporary PQ db")
    env["registry"].mongodb.pq_tenders.collection.delete_many({})
    logger.info("Successful flush!")


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
        help=("Limits the number of documents returned in one batch. Each batch requires a round trip to the server."),
    )
    commands = ["all", "run", "create_temporary_db", "flush_temporary_db", "revert_tenders"]
    default_cmd = commands[0]
    parser.add_argument(
        "--cmd",
        choices=commands,
        default=default_cmd,
        nargs="?",
        help=f"Provide cmd to run: {', '.join(commands)}",
    )
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        if args.cmd in ("all", "create_temporary_db"):
            create_temporary_db(env)
        if args.cmd in ("all", "run"):
            run(env, args)
        if args.cmd == "flush_temporary_db":
            flush_temporary_database(env)
        if args.cmd == "revert_tenders":
            revert_tenders(env, args)
