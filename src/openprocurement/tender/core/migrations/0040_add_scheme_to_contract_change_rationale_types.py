import logging
from datetime import datetime, timezone
from typing import Any
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.constants import (
    RATIONALE_TYPES_DECREE_1178,
    RATIONALE_TYPES_LAW_922,
    TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178,
)
from openprocurement.api.migrations.base import MigrationResult, PymongoCollectionMigration, migrate_collection

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

DATE_BEFORE_TYPES_SPLITTING = datetime(year=2022, month=10, day=12, tzinfo=timezone.utc)


def get_target_rationale_types(doc: dict) -> dict:
    """Determine the correct contractChangeRationaleTypes dict for a tender."""
    date_created_str = doc.get("dateCreated")
    if date_created_str:
        date_created = datetime.fromisoformat(date_created_str)
        if date_created.tzinfo is None:
            date_created = date_created.replace(tzinfo=timezone.utc)
        if date_created < DATE_BEFORE_TYPES_SPLITTING:
            return RATIONALE_TYPES_LAW_922

    pmt = doc.get("procurementMethodType", "")
    if pmt in TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178:
        return RATIONALE_TYPES_DECREE_1178

    if pmt == "reporting":
        cause_scheme = doc.get("causeDetails", {}).get("scheme")
        if cause_scheme in ("DECREE1178", "DECREE1275"):
            return RATIONALE_TYPES_DECREE_1178

    return RATIONALE_TYPES_LAW_922


def _needs_update(current: dict, target: dict) -> bool:
    """Return True if current contractChangeRationaleTypes differs from target."""
    if sorted(current.keys()) != sorted(target.keys()):
        return True
    first_entry = next(iter(current.values()), {})
    if "scheme" not in first_entry:
        return True
    target_entry: dict = next(iter(target.values()), {})
    target_scheme = target_entry.get("scheme")
    if first_entry.get("scheme") != target_scheme:
        return True
    return False


class Migration(PymongoCollectionMigration):
    """Add scheme field and refresh titles in contractChangeRationaleTypes for tenders and contracts."""

    description = "Add scheme to contractChangeRationaleTypes entries (tasks III+IV)"

    collection_name = "tenders"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self) -> dict:
        return {
            "contractChangeRationaleTypes": {"$exists": True},
        }

    def get_projection(self) -> dict:
        return {
            "procurementMethodType": 1,
            "dateCreated": 1,
            "causeDetails": 1,
            "contracts": 1,
            "contractChangeRationaleTypes": 1,
        }

    def process_data(self, cursor) -> MigrationResult:
        self.sub_migration = ContractSubMigration(self.settings, self.args)
        self.sub_result = MigrationResult()
        result = super().process_data(cursor)
        self.sub_migration.log_result(self.sub_result, action="Finished")
        return result

    def update_document(self, doc: dict, context: Any = None) -> dict | None:
        current = doc.get("contractChangeRationaleTypes")
        if not current:
            return None

        target_types = get_target_rationale_types(doc)

        # Collect and update contracts for this tender
        contract_docs = []
        for contract in doc.get("contracts", []):
            contract_id = contract.get("id") if isinstance(contract, dict) else None
            if not contract_id:
                continue
            contract_doc = self.sub_migration.collection.find_one(
                {"_id": contract_id},
                {"_id": 1, "_rev": 1, "contractChangeRationaleTypes": 1},
            )
            if contract_doc:
                contract_docs.append(contract_doc)

        if contract_docs:
            result = self.sub_migration.process_bulk(contract_docs, context={"target_types": target_types})
            self.sub_result += result

        if not _needs_update(current, target_types):
            return None

        doc["contractChangeRationaleTypes"] = dict(target_types)
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list[dict]:
        unset_pipeline = [{"$unset": "contractChangeRationaleTypes"}]
        return unset_pipeline + super().generate_base_pipeline_stages(doc)

    def run_test(self) -> None:
        mock_collection = self.run_test_data(
            [
                {
                    "_id": "aaa00000000000000000000000000001",
                    "_rev": "1-aaa00000000000000000000000000001",
                    "procurementMethodType": "negotiation",
                    "dateCreated": "2024-01-01T00:00:00+00:00",
                    "contractChangeRationaleTypes": {
                        "durationExtension": {
                            "title_uk": "old title",
                            "title_en": "old title en",
                            "description_uk": "desc",
                            "description_en": "desc en",
                        },
                    },
                    "contracts": [],
                },
                {
                    "_id": "aaa00000000000000000000000000002",
                    "_rev": "1-aaa00000000000000000000000000002",
                    "procurementMethodType": "reporting",
                    "dateCreated": "2024-01-01T00:00:00+00:00",
                    "causeDetails": {"scheme": "DECREE1275"},
                    "contractChangeRationaleTypes": {
                        "durationExtension": {
                            "title_uk": "old title",
                            "title_en": "old title en",
                            "description_uk": "desc",
                            "description_en": "desc en",
                        },
                    },
                    "contracts": [],
                },
            ],
        )

        expected_law922_types = dict(RATIONALE_TYPES_LAW_922)
        expected_decree1178_types = dict(RATIONALE_TYPES_DECREE_1178)

        mock_collection.bulk_write.assert_called_once_with(
            [
                UpdateOne(
                    {
                        "_id": "aaa00000000000000000000000000001",
                        "_rev": "1-aaa00000000000000000000000000001",
                    },
                    [
                        {"$unset": "contractChangeRationaleTypes"},
                        {
                            "$set": {
                                "_id": "aaa00000000000000000000000000001",
                                "_rev": "1-aaa00000000000000000000000000001",
                                "procurementMethodType": "negotiation",
                                "dateCreated": "2024-01-01T00:00:00+00:00",
                                "contractChangeRationaleTypes": expected_law922_types,
                                "contracts": [],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                    ],
                ),
                UpdateOne(
                    {
                        "_id": "aaa00000000000000000000000000002",
                        "_rev": "1-aaa00000000000000000000000000002",
                    },
                    [
                        {"$unset": "contractChangeRationaleTypes"},
                        {
                            "$set": {
                                "_id": "aaa00000000000000000000000000002",
                                "_rev": "1-aaa00000000000000000000000000002",
                                "procurementMethodType": "reporting",
                                "dateCreated": "2024-01-01T00:00:00+00:00",
                                "causeDetails": {"scheme": "DECREE1275"},
                                "contractChangeRationaleTypes": expected_decree1178_types,
                                "contracts": [],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                    ],
                ),
            ]
        )


class ContractSubMigration(PymongoCollectionMigration):
    """Migrate contractChangeRationaleTypes in contracts collection."""

    description = "Add scheme to contractChangeRationaleTypes entries in contracts"

    collection_name = "contracts"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    def update_document(self, doc: dict, context: Any = None) -> dict | None:
        current = doc.get("contractChangeRationaleTypes")
        if not current:
            return None

        target_types = (context or {}).get("target_types")
        if not target_types:
            return None

        if not _needs_update(current, target_types):
            return None

        doc["contractChangeRationaleTypes"] = dict(target_types)
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list[dict]:
        unset_pipeline = [{"$unset": "contractChangeRationaleTypes"}]
        return unset_pipeline + super().generate_base_pipeline_stages(doc)


if __name__ == "__main__":
    migrate_collection(Migration)
