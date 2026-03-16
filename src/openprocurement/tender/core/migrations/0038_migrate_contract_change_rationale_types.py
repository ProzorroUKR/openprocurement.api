import logging

from pymongo import DESCENDING

from openprocurement.api.constants import RATIONALE_TYPES_DECREE_1178
from openprocurement.api.constants_env import CONTRACT_CHANGE_RATIONALE_TYPES_SET_FROM
from openprocurement.api.migrations.base import (
    CollectionMigration,
    MigrationResult,
    migrate_collection,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    """Main migration: migrate contractChangeRationaleTypes in tenders and their contracts."""

    description = "Migrate contractChangeRationaleTypes in tender/contract (tender main migration)"

    collection_name = "tenders"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    CUTOFF_DATETIME = CONTRACT_CHANGE_RATIONALE_TYPES_SET_FROM
    CUTOFF_TIMESTAMP = int(CUTOFF_DATETIME.timestamp())

    def get_filter(self) -> dict:
        return {
            "procurementMethodType": "reporting",
            "causeDetails.scheme": "DECREE1178",
            "public_modified": {"$gte": self.CUTOFF_TIMESTAMP},
        }

    def get_projection(self) -> dict:
        return {
            "procurementMethodType": 1,
            "causeDetails": 1,
            "contracts": 1,
            "contractChangeRationaleTypes": 1,
        }

    def process_data(self, cursor):
        # Prepare sub migration
        self.sub_migration = ContractSubMigration(self.env, self.args)
        self.sub_result = MigrationResult()

        # Do migration
        cursor.sort([("public_modified", DESCENDING)])
        result = super().process_data(cursor)

        # Log sub migration result
        self.sub_migration.log_result(self.sub_result, action="Finished")

        return result

    def update_document(self, doc, context=None):
        # Iterate over all contracts in tender
        contract_docs = []
        for contract in doc.get("contracts", []):
            contract_id = contract.get("id") if isinstance(contract, dict) else None
            if not contract_id:
                continue

            # Find related contract
            contract_doc = self.sub_migration.collection.find_one(
                {"_id": contract_id},
                {"_id": 1, "_rev": 1, "contractChangeRationaleTypes": 1},
            )
            if not contract_doc:
                continue

            contract_docs.append(contract_doc)

        # Migrate contracts
        result = self.sub_migration.process_data(contract_docs)
        self.sub_result += result

        # Get current tender contractChangeRationaleTypes
        current = doc.get("contractChangeRationaleTypes")

        # Do not migrate if contractChangeRationaleTypes is not set
        if not current:
            return

        # Skip if contractChangeRationaleTypes is already set to the correct values
        current_keys = sorted(current.keys()) if current else []
        intended_keys = sorted(RATIONALE_TYPES_DECREE_1178.keys())
        if current_keys == intended_keys:
            return

        # Update contractChangeRationaleTypes
        doc["contractChangeRationaleTypes"] = dict(RATIONALE_TYPES_DECREE_1178)

        # Return the updated document
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list[dict]:
        # MongoDB $set merges nested objects; $unset then $set forces full replace.
        unset_pipeline = [{"$unset": "contractChangeRationaleTypes"}]
        return unset_pipeline + super().generate_base_pipeline_stages(doc)


class ContractSubMigration(CollectionMigration):
    """Migrate contractChangeRationaleTypes in contracts collection."""

    description = "Migrate contractChangeRationaleTypes in tender/contract (contract sub migration)"

    collection_name = "contracts"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    def update_document(self, doc, context=None):
        # Get current contract contractChangeRationaleTypes
        current = doc.get("contractChangeRationaleTypes")

        # Do not migrate if contractChangeRationaleTypes is not set
        if not current:
            return

        # Skip if contractChangeRationaleTypes is already set to the correct values
        current_keys = sorted(current.keys()) if current else []
        intended_keys = sorted(RATIONALE_TYPES_DECREE_1178.keys())
        if current_keys == intended_keys:
            return

        # Update contractChangeRationaleTypes
        doc["contractChangeRationaleTypes"] = dict(RATIONALE_TYPES_DECREE_1178)

        # Return the updated document
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list[dict]:
        # MongoDB $set merges nested objects; $unset then $set forces full replace.
        unset_pipeline = [{"$unset": "contractChangeRationaleTypes"}]
        return unset_pipeline + super().generate_base_pipeline_stages(doc)


if __name__ == "__main__":
    migrate_collection(Migration)
