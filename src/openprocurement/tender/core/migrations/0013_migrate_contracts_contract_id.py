import logging
import os

from pymongo.errors import OperationFailure

from openprocurement.api.migrations.base import BaseMigration, migrate

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migrate contractID to tender contracts: %s", migration_name)

    contracts_collection = env["registry"].mongodb.contracts.collection
    tenders_collection = env["registry"].mongodb.tenders.collection

    logger.info("Global contracts migration.")

    log_every = 100000
    count = 0

    cursor = tenders_collection.find(
        {"contracts": {"$exists": True}, "contracts.contractID": {"$exists": False}},
        {"contracts": 1},
    )

    cursor.batch_size(args.b)

    try:
        for tender in cursor:
            if not tender.get("contracts"):
                continue

            contracts_ids = [i["id"] for i in tender["contracts"]]

            contract_ids = {
                i["_id"]: i["contractID"]
                for i in contracts_collection.find({"_id": {"$in": contracts_ids}}, {"contractID": 1})
                if i.get("contractID")
            }

            for contract in tender["contracts"]:
                contract_id = contract_ids.get(contract.get("id"))
                if contract_id:
                    contract["contractID"] = contract_id

            try:
                tenders_collection.update_one(
                    {"_id": tender["_id"]},
                    {
                        "$set": {
                            "contracts": tender["contracts"],
                        },
                    },
                )
                count += 1
                if count % log_every == 0:
                    logger.info(f"Updating tenders with contract.contractID: updated {count} tenders")
            except OperationFailure as e:
                logger.warning(f"Skip updating tender {tender['_id']}. Details: {e}")
    finally:
        cursor.close()

    logger.info(f"Successful migration: {migration_name}, results: {count}  contracts")


class Migration(BaseMigration):
    def run(self):
        run(self.env, self.args)


if __name__ == "__main__":
    migrate(Migration)
