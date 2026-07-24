import logging
from typing import Any
from unittest.mock import ANY, MagicMock, patch

from pymongo import UpdateOne

from openprocurement.api.constants import (
    CAUSE_TO_RATIONALE_TYPES_MAPPING_ALL,
    RATIONALE_TYPES_DECREE_1178,
    RATIONALE_TYPES_LAW_922,
)
from openprocurement.api.migrations.base import MigrationResult, PymongoCollectionMigration, migrate_collection
from openprocurement.contracting.core.procedure.serializers.rationale_types import (
    enrich_contract_change_rationale_types,
    get_change_rationale_types_reference,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(PymongoCollectionMigration):
    description = "Add scheme/uri to contractChangeRationaleTypes in tender/contract (tender main migration)"

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

        mapping = CAUSE_TO_RATIONALE_TYPES_MAPPING_ALL
        rationale_types_reference = get_change_rationale_types_reference(doc, mapping)
        enriched = enrich_contract_change_rationale_types(current, rationale_types_reference)

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
            result = self.sub_migration.process_bulk(contract_docs, context={"tender": doc})
            self.sub_result += result

        if not enriched or enriched == current:
            return None

        doc["contractChangeRationaleTypes"] = enriched
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list[dict]:
        unset_pipeline = [{"$unset": "contractChangeRationaleTypes"}]
        return unset_pipeline + super().generate_base_pipeline_stages(doc)

    def run_test(self) -> None:
        old_entry = {
            "title_uk": "old title",
            "title_en": "old title en",
            "description_uk": "desc",
            "description_en": "desc en",
        }
        expected_law922_enriched = {
            "durationExtension": {
                **old_entry,
                "scheme": RATIONALE_TYPES_LAW_922["durationExtension"]["scheme"],
                "uri": RATIONALE_TYPES_LAW_922["durationExtension"]["uri"],
            },
        }
        expected_decree1178_enriched = {
            "durationExtension": {
                **old_entry,
                "scheme": RATIONALE_TYPES_DECREE_1178["durationExtension"]["scheme"],
                "uri": RATIONALE_TYPES_DECREE_1178["durationExtension"]["uri"],
            },
        }
        law922_without_uri = {
            code: {key: value for key, value in entry.items() if key != "uri"}
            for code, entry in RATIONALE_TYPES_LAW_922.items()
        }
        expected_law922_types = dict(RATIONALE_TYPES_LAW_922)

        contract_id = "bbb00000000000000000000000000001"
        contract_doc = {
            "_id": contract_id,
            "_rev": "1-bbb00000000000000000000000000001",
            "contractChangeRationaleTypes": {
                "durationExtension": dict(old_entry),
            },
        }
        mock_contracts_collection = MagicMock()
        mock_contracts_collection.find_one.return_value = contract_doc

        with patch.object(ContractSubMigration, "get_collection", return_value=mock_contracts_collection):
            mock_collection = self.run_test_data(
                [
                    {
                        "_id": "aaa00000000000000000000000000001",
                        "_rev": "1-aaa00000000000000000000000000001",
                        "procurementMethodType": "negotiation",
                        "dateCreated": "2024-01-01T00:00:00+00:00",
                        "contractChangeRationaleTypes": {
                            "durationExtension": dict(old_entry),
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
                            "durationExtension": dict(old_entry),
                        },
                        "contracts": [],
                    },
                    {
                        "_id": "aaa00000000000000000000000000003",
                        "_rev": "1-aaa00000000000000000000000000003",
                        "procurementMethodType": "negotiation.quick",
                        "dateCreated": "2024-01-01T00:00:00+00:00",
                        "causeDetails": {"scheme": "DECREE1178"},
                        "contractChangeRationaleTypes": {
                            "durationExtension": dict(old_entry),
                        },
                        "contracts": [{"id": contract_id}],
                    },
                    {
                        "_id": "aaa00000000000000000000000000004",
                        "_rev": "1-aaa00000000000000000000000000004",
                        "procurementMethodType": "negotiation",
                        "dateCreated": "2024-01-01T00:00:00+00:00",
                        "causeDetails": {"scheme": "LAW922"},
                        "contractChangeRationaleTypes": law922_without_uri,
                        "contracts": [],
                    },
                ],
            )

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
                                "contractChangeRationaleTypes": expected_law922_enriched,
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
                                "contractChangeRationaleTypes": expected_decree1178_enriched,
                                "contracts": [],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                    ],
                ),
                UpdateOne(
                    {
                        "_id": "aaa00000000000000000000000000003",
                        "_rev": "1-aaa00000000000000000000000000003",
                    },
                    [
                        {"$unset": "contractChangeRationaleTypes"},
                        {
                            "$set": {
                                "_id": "aaa00000000000000000000000000003",
                                "_rev": "1-aaa00000000000000000000000000003",
                                "procurementMethodType": "negotiation.quick",
                                "dateCreated": "2024-01-01T00:00:00+00:00",
                                "causeDetails": {"scheme": "DECREE1178"},
                                "contractChangeRationaleTypes": expected_decree1178_enriched,
                                "contracts": [{"id": contract_id}],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                    ],
                ),
                UpdateOne(
                    {
                        "_id": "aaa00000000000000000000000000004",
                        "_rev": "1-aaa00000000000000000000000000004",
                    },
                    [
                        {"$unset": "contractChangeRationaleTypes"},
                        {
                            "$set": {
                                "_id": "aaa00000000000000000000000000004",
                                "_rev": "1-aaa00000000000000000000000000004",
                                "procurementMethodType": "negotiation",
                                "dateCreated": "2024-01-01T00:00:00+00:00",
                                "causeDetails": {"scheme": "LAW922"},
                                "contractChangeRationaleTypes": expected_law922_types,
                                "contracts": [],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                    ],
                ),
            ]
        )

        mock_contracts_collection.find_one.assert_called_once_with(
            {"_id": contract_id},
            {"_id": 1, "_rev": 1, "contractChangeRationaleTypes": 1},
        )
        mock_contracts_collection.bulk_write.assert_called_once_with(
            [
                UpdateOne(
                    {
                        "_id": contract_id,
                        "_rev": "1-bbb00000000000000000000000000001",
                    },
                    [
                        {"$unset": "contractChangeRationaleTypes"},
                        {
                            "$set": {
                                "_id": contract_id,
                                "_rev": "1-bbb00000000000000000000000000001",
                                "contractChangeRationaleTypes": expected_decree1178_enriched,
                            }
                        },
                        {"$set": {"_rev": ANY}},
                        {
                            "$set": {
                                "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                                "public_ts": "$$CLUSTER_TIME",
                            }
                        },
                    ],
                ),
            ]
        )


class ContractSubMigration(PymongoCollectionMigration):
    description = "Add scheme/uri to contractChangeRationaleTypes in tender/contract (contract sub migration)"

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

        tender = (context or {}).get("tender")
        if not tender:
            return None

        mapping = CAUSE_TO_RATIONALE_TYPES_MAPPING_ALL
        rationale_types_reference = get_change_rationale_types_reference(tender, mapping)
        enriched = enrich_contract_change_rationale_types(current, rationale_types_reference)
        if not enriched or enriched == current:
            return None

        doc["contractChangeRationaleTypes"] = enriched
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list[dict]:
        unset_pipeline = [{"$unset": "contractChangeRationaleTypes"}]
        return unset_pipeline + super().generate_base_pipeline_stages(doc)


if __name__ == "__main__":
    migrate_collection(Migration)
