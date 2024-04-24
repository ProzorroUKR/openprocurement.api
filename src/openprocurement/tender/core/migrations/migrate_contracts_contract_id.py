# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import argparse
import logging
import os

from pymongo.errors import OperationFailure
from pyramid.paster import bootstrap

from openprocurement.api.constants import BASE_DIR

logging.basicConfig(level=logging.INFO, format='%(message)s')
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
        {"contracts.contractID": {"$exists": False}},
        {"contracts": 1},
    )

    cursor.batch_size(args.b)

    try:
        for tender in cursor:

            contracts_ids = [i["id"] for i in tender["contracts"]]

            contract_ids = {
                i["_id"]: i["contractID"]
                for i in contracts_collection.find({"_id": {"$in": contracts_ids}}, {"contractID": 1})
            }

            for contract in tender["contracts"]:
                contract["contractID"] = contract_ids.get(contract["id"])

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
