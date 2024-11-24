# pylint: disable=wrong-import-position

if __name__ == "__main__":
    from gevent import monkey

    monkey.patch_all(thread=False, select=False)

import logging
import os
from datetime import datetime

from pyramid.paster import bootstrap

from openprocurement.api.migrations.base import MigrationArgumentParser
from openprocurement.tender.core.procedure.utils import contracts_allow_to_complete

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# date of 2.6.202 release
DATE = datetime(year=2023, month=6, day=6)
BLOCK_COMPLAINT_STATUS = ("answered", "pending")


def tender_switch_status(tender):
    statuses = {lot.get("status") for lot in tender.get("lots", [])}
    if statuses == {"cancelled"}:
        tender["status"] = "cancelled"
    elif not statuses - {"unsuccessful", "cancelled"}:
        tender["status"] = "unsuccessful"
    if not statuses - {"complete", "unsuccessful", "cancelled"}:
        tender["status"] = "complete"


def tender_has_complaints(tender):
    for complaint in tender.get("complaints", []):
        if complaint.get("status", "") in BLOCK_COMPLAINT_STATUS and complaint.get("relatedLot") is None:
            return True
    return False


def check_award_lot_complaints(tender: dict, lot_id: str, lot_awards: list) -> bool:
    pending_complaints = False
    for complaint in tender.get("complaints", []):
        if complaint["status"] in BLOCK_COMPLAINT_STATUS and complaint.get("relatedLot") == lot_id:
            pending_complaints = True
            break

    pending_awards_complaints = False
    for award in lot_awards:
        for complaint in award.get("complaints", []):
            if complaint.get("status") in BLOCK_COMPLAINT_STATUS:
                pending_awards_complaints = True
                break
    if pending_complaints or pending_awards_complaints:
        return False
    return True


def run(env, args):
    migration_name = os.path.basename(__file__).split(".")[0]

    logger.info("Starting migration: %s", migration_name)

    collection = env["registry"].mongodb.tenders.collection

    logger.info("Updating completed tenders with disabled hasAwardingOrder")

    log_every = 100000
    count = 0

    cursor = collection.find(
        {
            "public_modified": {"$gte": DATE.timestamp()},
            "is_public": True,
            "config.hasAwardingOrder": False,
            "status": "active.awarded",
            "lots": {"$exists": True},
            "contracts.status": {"$ne": "pending"},
        },
        {"lots": 1, "contracts": 1, "awards": 1, "status": 1, "agreements": 1, "complaints": 1, "_rev": 1},
        no_cursor_timeout=True,
    )
    cursor.batch_size(args.b)
    try:
        modified_tenders = []
        for tender in cursor:
            if tender_has_complaints(tender):
                continue
            lots = tender.get("lots", [])
            updated = False
            contract_dates = []
            for lot in lots:
                if lot.get("status") == "active":
                    lot_awards = []
                    for a in tender.get("awards", []):
                        if a.get("lotID") == lot.get("id"):
                            lot_awards.append(a)
                    if not lot_awards:
                        continue
                    awards_statuses = {award["status"] for award in lot_awards}
                    if not check_award_lot_complaints(tender, lot["id"], lot_awards):
                        continue
                    elif not awards_statuses.intersection({"active", "pending"}):
                        continue
                    if awards_statuses.intersection({"active"}):
                        active_award_ids = {award["id"] for award in lot_awards if award["status"] == "active"}
                        contracts = [
                            contract
                            for contract in tender.get("contracts", [])
                            if contract.get("awardID") in active_award_ids
                        ]
                        allow_complete_lot = contracts_allow_to_complete(contracts)
                        if allow_complete_lot:
                            active_contract_date = [
                                datetime.fromisoformat(contract["date"])
                                for contract in contracts
                                if contract["status"] == "active"
                            ][0]
                            lot["status"] = "complete"
                            lot["date"] = active_contract_date.isoformat()
                            tender_switch_status(tender)
                            updated = True
                            contract_dates.append(active_contract_date)
            if updated:
                last_contract_date = max(contract_dates)
                collection.find_one_and_update(
                    {"_id": tender["_id"], "_rev": tender["_rev"]},
                    [
                        {
                            "$set": {
                                "lots": lots,
                                "status": tender["status"],
                                "date": last_contract_date.isoformat(),
                                "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                            }
                        }
                    ],
                )
                modified_tenders.append(tender["_id"])
                count += 1
                if count % log_every == 0:
                    logger.info(f"Updating completed tenders with disabled hasAwardingOrder: updated {count} tenders")
    finally:
        cursor.close()

    logger.info(f"Modified tenders: {modified_tenders}")
    logger.info(f"Updating completed tenders with disabled hasAwardingOrder finished: updated {count} tenders")

    logger.info(f"Successful migration: {migration_name}")


if __name__ == "__main__":
    parser = MigrationArgumentParser()
    args = parser.parse_args()
    with bootstrap(args.p) as env:
        run(env, args)
