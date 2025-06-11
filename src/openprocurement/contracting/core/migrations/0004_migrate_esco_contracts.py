# pylint: disable=wrong-import-position,wrong-import-order

import logging
import os
from collections import defaultdict

from pymongo.errors import OperationFailure

from openprocurement.api.context import set_request_now
from openprocurement.api.migrations.base import (
    BaseMigration,
    BaseMigrationArgumentParser,
    migrate,
)
from openprocurement.api.procedure.utils import append_revision, get_revision_changes
from openprocurement.contracting.core.procedure.models.contract import Buyer, Supplier
from openprocurement.tender.core.procedure.contracting import (
    clean_contract_value,
    clean_objs,
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def get_buyer(tender, contract):
    buyer = tender.get("procuringEntity", "")
    if contract.get("buyerID"):
        for i in tender.get("buyers", ""):
            if "id" in i and contract["buyerID"] == i.get("id", ""):
                buyer = i
                break

    clean_objs([buyer], Buyer, {"id", "contactPoint"})
    return buyer


def get_bid_credentials(tender, award_id):
    bid_id = next((a.get("bid_id", "") for a in tender.get("awards", []) if a.get("id") == award_id), "")
    bid = next((i for i in tender.get("bids", []) if i.get("id", "") == bid_id), tender)

    return bid["owner"], bid["owner_token"]


def create_contract(env, tender, tender_contract):
    if tender.get("mode"):
        tender_contract["mode"] = tender["mode"]
    if tender.get("config"):
        tender_contract["config"] = {"restricted": tender["config"]["restricted"]}

    bid_owner, bid_token = get_bid_credentials(tender, tender_contract.get("awardID"))

    if "value" in tender_contract:
        tender_contract["value"] = clean_contract_value(dict(tender_contract["value"]))

    tender_contract.update(
        {
            "buyer": get_buyer(tender, tender_contract),
            "tender_id": tender["_id"],
            "owner": tender["owner"],
            "tender_token": tender["owner_token"],
            "bid_owner": bid_owner,
            "bid_token": bid_token,
        }
    )

    patch = get_revision_changes(tender_contract, {})
    if patch:
        append_revision(env["request"], tender_contract, patch)
        try:
            env["registry"].mongodb.contracts.save(
                tender_contract,
                insert=True,
                modified=True,
            )
            return True
        except OperationFailure as e:
            logger.warning(f"Skip updating contract {tender_contract['id']}. Details: {e}")


def update_contract_pe_to_buyer(env, tender, tender_contract, contracting_contract):
    collection = env["registry"].mongodb.contracts.collection

    updated_data = {}

    if "bid_owner" not in contracting_contract or "bid_token" not in contracting_contract:
        bid_owner, bid_token = get_bid_credentials(tender, tender_contract.get("awardID"))
        updated_data["bid_owner"] = bid_owner
        updated_data["bid_token"] = bid_token

    if "suppliers" in contracting_contract:
        clean_objs(contracting_contract["suppliers"], Supplier, {"id", "contactPoint"})
        updated_data["suppliers"] = contracting_contract["suppliers"]

    if tender.get("mode") and not contracting_contract.get("mode"):
        updated_data["mode"] = tender["mode"]
        updated_data["is_test"] = updated_data["mode"] == "test"

    if "buyerID" not in contracting_contract and "buyerID" in tender_contract:
        updated_data["buyerID"] = contracting_contract["buyerID"] = tender_contract["buyerID"]

    if "procuringEntity" in contracting_contract or "buyerID" in updated_data:
        updated_data["buyer"] = get_buyer(tender, contracting_contract)

    if not updated_data:
        logger.warning(f"Skip updating contract {contracting_contract['_id']}. Details: Contract up to date")
        return

    try:
        collection.update_one(
            {"_id": contracting_contract["_id"]},
            {
                "$set": updated_data,
                "$unset": {"procuringEntity": ""},
            },
        )
        return True
    except OperationFailure as e:
        logger.warning(f"Skip updating contract {contracting_contract['_id']}. Details: {e}")


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting esco contracting migration: %s", migration_name)

    contracts_collection = env["registry"].mongodb.contracts.collection
    tenders_collection = env["registry"].mongodb.tenders.collection

    contract_statuses = args.s.split(",")

    logger.info("Global contracts migration.")

    log_every = 100000
    counter = defaultdict(total_contracts=0, updated_contracts=0, created_contracts=0, skipped_contracts=0)

    cursor = tenders_collection.find(
        {"contracts.status": {"$in": contract_statuses}, "procurementMethodType": "esco"},
        {
            "contracts": 1,
            "buyers": 1,
            "bids": 1,
            "awards": 1,
            "owner": 1,
            "owner_token": 1,
            "procuringEntity": 1,
            "mode": 1,
        },
    )

    cursor.batch_size(args.b)

    try:
        for tender in cursor:

            contracts_ids = [i["id"] for i in tender.get("contracts", "")]

            contracting_contracts = {
                i["_id"]: i
                for i in contracts_collection.find(
                    {"_id": {"$in": contracts_ids}},
                    {"procuringEntity": 1, "buyerID": 1, "bid_owner": 1, "bid_token": 1, "suppliers": 1, "mode": 1},
                )
            }

            for contract_number, contract in enumerate(tender.get("contracts", "")):
                if contract.get("status", "") not in contract_statuses:
                    continue

                contracting_contract = contracting_contracts.get(contract["id"])
                set_request_now()
                if not contracting_contract:
                    if create_contract(env, tender, contract):
                        counter["created_contracts"] += 1
                    else:
                        counter["skipped_contracts"] += 1
                else:
                    if update_contract_pe_to_buyer(env, tender, contract, contracting_contract):
                        counter["updated_contracts"] += 1
                    else:
                        counter["skipped_contracts"] += 1

                counter["total_contracts"] += 1

                if counter["total_contracts"] % log_every == 0:
                    logger.info(f"Updating contracts: results {counter} contracts")

    finally:
        cursor.close()

    logger.info(f"Successful migration: {migration_name}, results: {counter}")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


class MigrationArgumentParser(BaseMigrationArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument(
            "-s",
            default="pending",
            help=(
                "Contract statuses in which contract should be migrated. "
                "For few statuses separate it with ','. F.E: pending,active"
            ),
        )


if __name__ == "__main__":
    migrate(Migration, parser=MigrationArgumentParser)
