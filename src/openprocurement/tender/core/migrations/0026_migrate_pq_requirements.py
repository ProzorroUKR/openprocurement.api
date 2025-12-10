import logging
import os
import traceback
from copy import deepcopy
from decimal import Decimal

from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import BaseMigrationArgumentParser
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.constants import PQ

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def convert_expected_value_to_string(requirement):
    requirement["dataType"] = "string"
    requirement["expectedValues"] = [str(requirement.pop("expectedValue"))]
    requirement["expectedMinItems"] = 1


def normalize_expected_values(requirement):
    requirement["dataType"] = "string"
    requirement["expectedValues"] = [str(value) for value in requirement["expectedValues"]]
    requirement["expectedMinItems"] = 1


def convert_field_to_decimal(requirement, field_name):
    if isinstance(requirement[field_name], (float, int, Decimal)):
        requirement[field_name] = to_decimal(requirement[field_name])
        requirement["dataType"] = "number"
        return True
    return False


def pop_min_max_values(requirement):
    requirement.pop("maxValue", None)
    requirement.pop("minValue", None)


def convert_min_max_value_to_string(requirement):
    if "minValue" not in requirement:
        requirement["expectedValues"] = [str(requirement["maxValue"])]
    else:
        requirement["expectedValues"] = [str(requirement["minValue"]), str(requirement["maxValue"])]
    requirement["expectedMinItems"] = 1
    requirement["dataType"] = "string"
    pop_min_max_values(requirement)


def update_criteria_and_responses_integer(requirement):
    if "expectedValues" in requirement and requirement["expectedValues"]:  # not empty list
        normalize_expected_values(requirement)
    elif "maxValue" in requirement:
        if isinstance(requirement["maxValue"], (float, Decimal)):
            requirement["dataType"] = "number"
            if "minValue" not in requirement:  # add minValue to requirement
                requirement["minValue"] = 0
            else:
                convert_field_to_decimal(requirement, "minValue")
        elif not isinstance(requirement["maxValue"], int):
            convert_min_max_value_to_string(requirement)
        elif "minValue" not in requirement:  # add minValue to requirement
            requirement["minValue"] = 0
    elif "minValue" in requirement or "expectedValue" in requirement:
        for field_name in ("minValue", "expectedValue"):
            if field_name in requirement:
                if isinstance(requirement[field_name], (float, Decimal)):
                    requirement["dataType"] = "number"
                elif field_name == "expectedValue" and isinstance(requirement["expectedValue"], (bool, str)):
                    convert_expected_value_to_string(requirement)
    else:
        requirement["minValue"] = 0
        for field_name in ("expectedValues", "expectedMinItems", "expectedMaxItems"):
            requirement.pop(field_name, None)


def update_criteria_and_responses_number(requirement):
    if "expectedValues" in requirement and requirement["expectedValues"]:  # not empty list
        normalize_expected_values(requirement)
    elif "maxValue" in requirement:
        if convert_field_to_decimal(requirement, "maxValue"):
            if "minValue" not in requirement:  # add minValue to requirement
                requirement["minValue"] = 0
            else:
                convert_field_to_decimal(requirement, "minValue")
        else:
            convert_min_max_value_to_string(requirement)
    elif "minValue" in requirement or "expectedValue" in requirement:
        for field_name in ("minValue", "expectedValue"):
            if field_name in requirement:
                if field_name == "expectedValue" and isinstance(requirement["expectedValue"], (bool, str)):
                    convert_expected_value_to_string(requirement)
                else:
                    convert_field_to_decimal(requirement, field_name)
    else:
        requirement["minValue"] = 0
        for field_name in ("expectedValues", "expectedMinItems", "expectedMaxItems"):
            requirement.pop(field_name, None)


def update_criteria_and_responses_string(requirement):
    if "expectedValues" in requirement and requirement["expectedValues"]:  # not empty list
        normalize_expected_values(requirement)
    elif "expectedValue" in requirement:
        convert_expected_value_to_string(requirement)
    # maxValue + minValue одночасно
    elif "minValue" in requirement and "maxValue" in requirement:
        requirement["expectedValues"] = [str(requirement["minValue"]), str(requirement["maxValue"])]
        requirement["expectedMinItems"] = 1
        pop_min_max_values(requirement)
    elif "minValue" in requirement or "maxValue" in requirement:
        for field_name in ("minValue", "maxValue"):
            if field_name in requirement:
                requirement["expectedValues"] = [str(requirement[field_name])]
                requirement["expectedMinItems"] = 1
                pop_min_max_values(requirement)


def update_criteria_and_responses_boolean(requirement):
    if "expectedValues" in requirement:
        if len(requirement["expectedValues"]) == 1:
            if isinstance(requirement["expectedValues"][0], bool):
                requirement["expectedValue"] = requirement["expectedValues"][0]
                for field_name in ("expectedValues", "expectedMinItems", "expectedMaxItems"):
                    requirement.pop(field_name, None)
        elif set(requirement["expectedValues"]) == {True, False}:
            for field_name in ("expectedValues", "expectedMinItems", "expectedMaxItems"):
                requirement.pop(field_name, None)
        # check whether expectedValues is left
        if requirement.get("expectedValues"):
            normalize_expected_values(requirement)
    elif "expectedValue" in requirement and not isinstance(requirement["expectedValue"], bool):
        convert_expected_value_to_string(requirement)


def update_criteria(criteria: list, bids: list):
    if not criteria:
        return [], bids
    updated_criteria = []
    updated = False

    for criterion in criteria:
        updated_criterion = deepcopy(criterion)
        for req_group in updated_criterion.get("requirementGroups", []):
            for requirement in req_group.get("requirements", []):
                previous_requirement = deepcopy(requirement)
                # Remove min/max values if expected values exist
                if ("expectedValue" in requirement or "expectedValues" in requirement) and (
                    "minValue" in requirement or "maxValue" in requirement
                ):
                    pop_min_max_values(requirement)
                # Handle different data types
                if requirement["dataType"] == "integer":
                    update_criteria_and_responses_integer(requirement)
                elif requirement["dataType"] == "number":
                    update_criteria_and_responses_number(requirement)
                elif requirement["dataType"] == "string":
                    update_criteria_and_responses_string(requirement)
                elif requirement["dataType"] == "boolean":
                    update_criteria_and_responses_boolean(requirement)

                # delete unit from string and boolean requirements
                if requirement["dataType"] in ("string", "boolean"):
                    requirement.pop("unit", None)
                if requirement != previous_requirement:
                    updated = True
        updated_criteria.append(updated_criterion)
    return updated_criteria if updated else None


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
            try:
                bids = tender.get("bids", [])
                updated_criteria = update_criteria(tender["criteria"], bids)
                if updated_criteria:
                    collection.update_one(
                        {"_id": tender["_id"]},
                        {
                            "$set": {
                                "dateModified": now.isoformat(),
                                "public_modified": now.timestamp(),
                                "criteria": updated_criteria,
                                "bids": bids,
                            }
                        },
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
    parser = BaseMigrationArgumentParser()
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
