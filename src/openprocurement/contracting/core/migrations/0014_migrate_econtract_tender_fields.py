import logging
from unittest.mock import ANY, MagicMock, call, patch

from pymongo import DESCENDING, UpdateOne

from openprocurement.api.migrations.base import (
    PymongoCollectionMigration,
    ReadonlyCollectionWrapper,
    migrate_collection,
)
from openprocurement.contracting.core.procedure.models.access import AccessRole

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

TENDER_FIELDS = ("tenderID", "mainProcurementCategory")
TENDER_PROJECTION = {"tenderID": 1, "mainProcurementCategory": 1}


def sorted_changes(operations: list) -> list:
    """Revision changes come from a dict diff, so their order is not stable; sort them by path."""
    for operation in operations:
        for stage in operation._doc:
            revisions = stage.get("$set", {}).get("revisions")
            if revisions:
                revisions[-1]["changes"] = sorted(revisions[-1]["changes"], key=lambda change: change["path"])
    return operations


class Migration(PymongoCollectionMigration):
    """Copy tenderID and mainProcurementCategory from tender to eContracts.

    eContracts are moved up in the feed (public_modified is updated),
    so feed consumers see the new fields.
    """

    description = "Copy tenderID and mainProcurementCategory from tender to eContracts"

    collection_name = "contracts"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = True

    def process_data(self, cursor):
        cursor.sort([("public_modified", DESCENDING)])
        return super().process_data(cursor)

    def get_filter(self) -> dict:
        return {
            # tenderID is always set together with mainProcurementCategory (when tender has it),
            # so its absence marks a contract that was not migrated yet
            "tenderID": {"$exists": False},
            # eContract: has buyer/supplier access roles (see ContractTypePredicate)
            "access.role": {"$in": [AccessRole.BUYER.value, AccessRole.SUPPLIER.value]},
        }

    def get_projection(self):
        return {"tender_id": 1, "tenderID": 1, "mainProcurementCategory": 1}

    def _get_tenders_collection(self):
        return ReadonlyCollectionWrapper(self.db_store.tenders.collection)

    @property
    def _tenders_collection(self):
        return self._get_tenders_collection()

    def _get_tenders(self, tender_ids: set) -> dict:
        """Fetch tenders of the whole bulk with one query."""
        if not tender_ids:
            return {}
        cursor = self._tenders_collection.find({"_id": {"$in": sorted(tender_ids)}}, TENDER_PROJECTION)
        return {tender["_id"]: tender for tender in cursor}

    def process_bulk(self, bulk, context=None):
        tender_ids = {doc["tender_id"] for doc in bulk if doc.get("tender_id")}
        context = {"tenders": self._get_tenders(tender_ids)}
        return super().process_bulk(bulk, context=context)

    def _get_tender(self, tender_id, context):
        return context["tenders"].get(tender_id)

    def update_document(self, doc, context=None):
        tender_id = doc.get("tender_id")
        if not tender_id:
            logger.warning(f"Contract {doc['_id']} has no tender_id, skipped")
            return None

        tender = self._get_tender(tender_id, context)
        if not tender:
            logger.warning(f"Tender {tender_id} not found for contract {doc['_id']}, skipped")
            return None

        if not tender.get("tenderID"):
            logger.warning(f"Tender {tender_id} has no tenderID, contract {doc['_id']} skipped")
            return None

        if not tender.get("mainProcurementCategory"):
            logger.info(f"Tender {tender_id} has no mainProcurementCategory, contract {doc['_id']} gets tenderID only")

        updated = False
        for field in TENDER_FIELDS:
            # keep already filled fields untouched
            if field not in doc and tender.get(field):
                doc[field] = tender[field]
                updated = True

        if not updated:
            return None

        logger.info(f"Set tender fields in contract {doc['_id']}: {[field for field in TENDER_FIELDS if field in doc]}")
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list:
        # update only the new fields and revisions, not the whole document
        fields = {field: doc[field] for field in TENDER_FIELDS if field in doc}
        return [{"$set": {**fields, "revisions": doc["revisions"]}}]

    def run_test(self):
        tender_1_id = "3ea0465206d14304aa0eece4f8e1a2a4"
        tender_2_id = "5b20cae130a3465abe4e09d7d7cd2e39"
        tender_3_id = "3d87690ac08c43049452db8f89ef6811"
        tender_4_id = "7c1d5e0f4a3b4c2d9e8f7a6b5c4d3e2f"

        contract_1_id = "a48fdc49cfed438fbb2880b287178ced"
        contract_2_id = "541456190016476a8e62164bd3593980"
        contract_3_id = "50de2cd1e67c4c2b974b6b2fd3efa299"
        contract_4_id = "1f2e3d4c5b6a49788a9b0c1d2e3f4a5b"
        contract_5_id = "9a8b7c6d5e4f43219a8b7c6d5e4f4321"

        revisions = [
            {
                "author": "broker",
                "changes": [],
                "rev": None,
                "date": "2026-07-01T10:00:00.000000+03:00",
            }
        ]
        rev = "7-5ae2fd5ee31142ad8bb203b04c434e4e"

        contracts = [
            # tender has both fields
            {"_id": contract_1_id, "_rev": rev, "revisions": revisions, "tender_id": tender_1_id},
            # tender has no mainProcurementCategory
            {"_id": contract_2_id, "_rev": rev, "revisions": revisions, "tender_id": tender_2_id},
            # tender not found
            {"_id": contract_3_id, "_rev": rev, "revisions": revisions, "tender_id": tender_3_id},
            # contract has no tender_id
            {"_id": contract_4_id, "_rev": rev, "revisions": revisions},
            # mainProcurementCategory already set, only tenderID is added
            {
                "_id": contract_5_id,
                "_rev": rev,
                "revisions": revisions,
                "tender_id": tender_4_id,
                "mainProcurementCategory": "works",
            },
        ]
        tenders = [
            {"_id": tender_1_id, "tenderID": "UA-2026-07-01-000001-a", "mainProcurementCategory": "goods"},
            {"_id": tender_2_id, "tenderID": "UA-2026-07-01-000002-a"},
            {"_id": tender_4_id, "tenderID": "UA-2026-07-01-000004-a", "mainProcurementCategory": "services"},
        ]

        mock_tenders_collection = MagicMock(find=MagicMock(return_value=iter(tenders)))

        with patch.object(self, "_get_tenders_collection", return_value=mock_tenders_collection):
            mock_collection = self.run_test_data(contracts)

        # tenders of the whole bulk are fetched with a single query
        assert mock_tenders_collection.find.call_args_list == [
            call({"_id": {"$in": sorted([tender_1_id, tender_2_id, tender_3_id, tender_4_id])}}, TENDER_PROJECTION),
        ]

        feed_position_stage = {
            "$set": {
                "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                "public_ts": "$$CLUSTER_TIME",
            }
        }

        assert sorted_changes(mock_collection.bulk_write.call_args[0][0]) == sorted_changes(
            [
                UpdateOne(
                    {"_id": contract_1_id, "_rev": rev},
                    [
                        {
                            "$set": {
                                "tenderID": "UA-2026-07-01-000001-a",
                                "mainProcurementCategory": "goods",
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/tenderID"},
                                            {"op": "remove", "path": "/mainProcurementCategory"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                        feed_position_stage,
                    ],
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
                UpdateOne(
                    {"_id": contract_2_id, "_rev": rev},
                    [
                        {
                            "$set": {
                                "tenderID": "UA-2026-07-01-000002-a",
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/tenderID"}],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                        feed_position_stage,
                    ],
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
                UpdateOne(
                    {"_id": contract_5_id, "_rev": rev},
                    [
                        {
                            "$set": {
                                "tenderID": "UA-2026-07-01-000004-a",
                                "mainProcurementCategory": "works",
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/tenderID"}],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                        feed_position_stage,
                    ],
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
            ]
        )


if __name__ == "__main__":
    migrate_collection(Migration)
