import logging
import re
from datetime import datetime, timezone

from pymongo import DESCENDING

from openprocurement.api.migrations.base import (
    CollectionMigration,
    ReadonlyCollectionWrapper,
    migrate_collection,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Fix contractID format: add missing 'a' prefix before contract number"

    collection_name = "contracts"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    # Cutoff time: 29 January 2026 18:00 Kyiv time (EET, UTC+2)
    # Convert to UTC: 29 January 2026 16:00 UTC
    CUTOFF_DATETIME = datetime(2026, 1, 29, 16, 0, 0, tzinfo=timezone.utc)
    CUTOFF_TIMESTAMP = int(CUTOFF_DATETIME.timestamp())

    def process_data(self, cursor):
        cursor.sort([("public_modified", DESCENDING)])
        super().process_data(cursor)

    def get_filter(self) -> dict:
        return {
            "is_public": True,
            "contractID": {"$regex": r"-a-\d+$"},
            "public_modified": {"$gte": self.CUTOFF_TIMESTAMP},
        }

    def get_projection(self):
        return {"contractID": 1, "tender_id": 1}

    def _get_tenders_collection(self):
        return ReadonlyCollectionWrapper(getattr(self.env["registry"].mongodb, "tenders").collection)

    @property
    def _tenders_collection(self):
        return self._get_tenders_collection()

    def update_document(self, doc, context=None):
        contract_id = doc.get("contractID", "")
        if not contract_id:
            return None

        # UA-2026-01-29-019184-a-1 -> UA-2026-01-29-019184-a-a1
        pattern = r"(-a-)(\d+)$"
        match = re.search(pattern, contract_id)
        if match:
            # Replace -a-<number> with -a-a<number>
            fixed_contract_id = re.sub(pattern, r"\1a\2", contract_id)
            doc["contractID"] = fixed_contract_id

            # Update contractID in tender.contracts array
            tender_id = doc.get("tender_id")
            if tender_id:
                self.update_tender(tender_id, doc["_id"], fixed_contract_id)

            logger.info(f"Fixed contractID in contract {doc['_id']}: {contract_id} -> {fixed_contract_id}")
            return doc

        return None

    def update_tender(self, tender_id, contract_id, fixed_contract_id):
        tender = self._tenders_collection.find_one(
            {"_id": tender_id},
            {"contracts": 1, "_rev": 1},
        )
        if not tender or not tender.get("contracts"):
            return

        contracts = tender["contracts"]
        tender_rev = tender.get("_rev")
        updated = False

        # Find contract in tender.contracts array by id and update contractID
        for contract in contracts:
            if contract.get("id") == contract_id:
                old_contract_id = contract.get("contractID")
                if old_contract_id != fixed_contract_id:
                    contract["contractID"] = fixed_contract_id
                    updated = True
                    logger.info(
                        f"Updated contractID in tender {tender_id} for contract {contract_id}: {old_contract_id} -> {fixed_contract_id}"
                    )
                break

        # Update tender if contractID was changed
        if updated:
            tenders_collection = getattr(self.env["registry"].mongodb, "tenders").collection
            result = tenders_collection.update_one(
                {"_id": tender_id, "_rev": tender_rev},
                [
                    {"$set": {"contracts": contracts}},
                    {
                        "$set": {
                            "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                            "public_ts": "$$CLUSTER_TIME",
                        }
                    },
                ],
            )
            if result.matched_count == 0:
                logger.warning(f"Failed to update tender {tender_id}: revision conflict (expected _rev: {tender_rev})")


if __name__ == "__main__":
    migrate_collection(Migration)
