import logging
from importlib import import_module
from typing import Type
from unittest.mock import ANY, MagicMock, call, patch

from pymongo import UpdateOne

from openprocurement.api.migrations.base import PymongoCollectionMigration, migrate_collection

econtract_migration = import_module("openprocurement.contracting.core.migrations.0014_migrate_econtract_tender_fields")
BaseMigration: Type[PymongoCollectionMigration] = econtract_migration.Migration

TENDER_PROJECTION: dict = econtract_migration.TENDER_PROJECTION

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def sorted_changes(operations: list) -> list:
    """Revision changes come from a dict diff, so their order is not stable; sort them by path."""
    for operation in operations:
        for stage in operation._doc:
            revisions = stage.get("$set", {}).get("revisions")
            if revisions:
                revisions[-1]["changes"] = sorted(revisions[-1]["changes"], key=lambda change: change["path"])
    return operations


class Migration(BaseMigration):
    """Copy tenderID and mainProcurementCategory from tender to all contracts.

    Same logic as 0014, but for every contract and without touching the feed position:
    contracts keep their public_modified, so there is no wave of updates in the feed.
    eContracts already migrated by 0014 are skipped by the filter.
    """

    description = "Copy tenderID and mainProcurementCategory from tender to all contracts"

    update_date_modified: bool = False
    update_feed_position: bool = False

    def get_filter(self) -> dict:
        return {"tenderID": {"$exists": False}}

    def run_test(self):
        tender_1_id = "3ea0465206d14304aa0eece4f8e1a2a4"
        tender_2_id = "5b20cae130a3465abe4e09d7d7cd2e39"

        contract_1_id = "a48fdc49cfed438fbb2880b287178ced"
        contract_2_id = "541456190016476a8e62164bd3593980"

        revisions = [
            {
                "author": "broker",
                "changes": [],
                "rev": None,
                "date": "2024-11-12T16:02:59.403731+02:00",
            }
        ]
        rev = "7-5ae2fd5ee31142ad8bb203b04c434e4e"

        contracts = [
            # tender has both fields
            {"_id": contract_1_id, "_rev": rev, "revisions": revisions, "tender_id": tender_1_id},
            # tender has no mainProcurementCategory
            {"_id": contract_2_id, "_rev": rev, "revisions": revisions, "tender_id": tender_2_id},
        ]
        tenders = [
            {"_id": tender_1_id, "tenderID": "UA-2024-11-12-000001-a", "mainProcurementCategory": "services"},
            {"_id": tender_2_id, "tenderID": "UA-2024-11-12-000002-a"},
        ]

        mock_tenders_collection = MagicMock(find=MagicMock(return_value=iter(tenders)))

        with patch.object(self, "_get_tenders_collection", return_value=mock_tenders_collection):
            mock_collection = self.run_test_data(contracts)

        assert mock_tenders_collection.find.call_args_list == [
            call({"_id": {"$in": sorted([tender_1_id, tender_2_id])}}, TENDER_PROJECTION),
        ]

        # no feed position stage: public_modified stays untouched
        assert sorted_changes(mock_collection.bulk_write.call_args[0][0]) == sorted_changes(
            [
                UpdateOne(
                    {"_id": contract_1_id, "_rev": rev},
                    [
                        {
                            "$set": {
                                "tenderID": "UA-2024-11-12-000001-a",
                                "mainProcurementCategory": "services",
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
                                "tenderID": "UA-2024-11-12-000002-a",
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
