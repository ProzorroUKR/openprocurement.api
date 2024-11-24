# pylint: disable=wrong-import-position
from copy import deepcopy
from datetime import datetime
from time import sleep

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os

from pymongo import UpdateOne
from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.api.procedure.models.document import ConfidentialityTypes
from openprocurement.api.utils import get_now
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Release 2.6.320 (release with confidential docs in contracting)
DATE = datetime(year=2024, month=7, day=29)


def open_confidential_docs(contract):
    updated_docs = []
    updated = False

    for doc in contract.get("documents", []):
        doc = deepcopy(doc)
        if doc.get("confidentiality") == ConfidentialityTypes.BUYER_ONLY.value:
            doc["confidentiality"] = ConfidentialityTypes.PUBLIC.value
            doc.pop("confidentialityRationale", None)
            updated = True
        updated_docs.append(doc)
    return updated_docs if updated else []


def bulk_update(bulk, collection):
    bulk_size = len(bulk)
    try:
        collection.bulk_write(bulk)
        return bulk_size
    except OperationFailure as e:
        logger.warning(f"Skip updating {bulk_size} contracts. Details: {e}")
        return 0


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    tender_collection = env["registry"].mongodb.tenders.collection
    contract_collection = env["registry"].mongodb.contracts.collection

    logger.info("Updating tender's complaints objections with sequenceNumber")

    log_every = 100000

    cursor = tender_collection.find(
        {
            "public_modified": {"$gte": DATE.timestamp()},
            "is_public": True,
            "procurementMethodType": {"$in": [REPORTING, NEGOTIATION, NEGOTIATION_QUICK]},
            "cause": "lastHope",
            "contracts": {"$exists": 1},
        },
        no_cursor_timeout=True,
    )

    cursor.batch_size(args.b)
    bulk = []
    updated_contracts_ids = []
    count = 0
    bulk_max_size = 500
    try:
        for tender in cursor:
            for contract_data in tender.get("contracts", []):
                contract = contract_collection.find_one(
                    {"_id": contract_data["id"]},
                    {"documents": 1, "_id": 1},
                    no_cursor_timeout=True,
                )

                if updated_docs := open_confidential_docs(contract):
                    bulk.append(
                        UpdateOne(
                            {"_id": contract["_id"]},
                            {
                                "$set": {
                                    "documents": updated_docs,
                                    "public_modified": get_now().timestamp(),
                                }
                            },
                        )
                    )
                    updated_contracts_ids.append(contract["_id"])

                if bulk and len(bulk) % bulk_max_size == 0:
                    count += bulk_update(bulk, contract_collection)
                    bulk = []

                    if count % log_every == 0:
                        logger.info(f"Updating contract's conf docs: {count} updated")

        sleep(0.000001)
    finally:
        cursor.close()

    if bulk:
        count += bulk_update(bulk, contract_collection)

    logger.info(f"Contract ids: {updated_contracts_ids}")
    logger.info(f"Updated {count} contracts")
    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
