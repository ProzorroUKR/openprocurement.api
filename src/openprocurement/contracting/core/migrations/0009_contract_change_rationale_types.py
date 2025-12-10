import logging
from datetime import datetime
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.constants import (
    RATIONALE_TYPES,
    RATIONALE_TYPES_DECREE_1178,
    RATIONALE_TYPES_LAW_922,
    TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178,
    TZ,
)
from openprocurement.api.migrations.base import CollectionMigration, migrate_collection

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


DATE_BEFORE_TYPES_SPLITTING = TZ.localize(datetime(year=2022, month=10, day=12))


class Migration(CollectionMigration):
    description = "Migrating contractChangeRationaleTypes"

    collection_name = "contracts"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {"contractChangeRationaleTypes": {"$exists": False}}

    def get_projection(self):
        return {"dateCreated": 1, "procurementMethodType": 1, "changes": 1}

    def update_document(self, doc, context=None):
        date_created = datetime.fromisoformat(doc["dateCreated"])
        if date_created < DATE_BEFORE_TYPES_SPLITTING:
            rationale_types = RATIONALE_TYPES
        elif doc["procurementMethodType"] in TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178:
            rationale_types = RATIONALE_TYPES_DECREE_1178
        else:
            rationale_types = RATIONALE_TYPES_LAW_922
        rationale_type_from_dict = True
        for change in doc.get("changes", []):
            for rationale_type in change.get("rationaleTypes", []):
                if rationale_type not in list(rationale_types.keys()):
                    logger.info(
                        f"ERROR: Contract with id {doc['_id']} has `{rationale_type}` in changes.rationaleTypes "
                        f"which doesn't match keys in dictionary"
                    )
                    rationale_type_from_dict = False
        if rationale_type_from_dict:
            doc["contractChangeRationaleTypes"] = rationale_types
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list:
        return [
            {
                "$set": {
                    "contractChangeRationaleTypes": doc["contractChangeRationaleTypes"],
                    "revisions": doc["revisions"],
                },
            },
        ]

    def run_test(self):
        mock_collection = self.run_test_data(
            [
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a2a4",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "dateCreated": "2022-01-01T00:00:00.00+03:00",
                    "procurementMethodType": "belowThreshold",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                },
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a2a5",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "dateCreated": "2022-10-11T23:59:59.00+03:00",
                    "procurementMethodType": "priceQuotation",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                },
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a2a6",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "dateCreated": "2023-01-01T00:00:00.00+03:00",
                    "procurementMethodType": "belowThreshold",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                },
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a2a7",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "dateCreated": "2025-01-01T00:00:00.00+03:00",
                    "procurementMethodType": "aboveThreshold",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                },
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a2a8",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "dateCreated": "2022-10-12T00:00:00.00+03:00",
                    "procurementMethodType": "priceQuotation",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                },
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a2a9",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "dateCreated": "2022-10-12T00:00:00.00+03:00",
                    "procurementMethodType": "esco",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                },
                # shouldn't be migrated, should be error in log
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a2a0",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "dateCreated": "2022-10-12T00:00:00.00+03:00",
                    "procurementMethodType": "priceQuotation",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                    "changes": [
                        {
                            "rationale": "Зміни № 2 Опис причини внесення змін до контракту",
                            "rationale_en": "Contract change cause",
                            "rationaleTypes": ["volumeCuts", "priceReduction"],
                            "status": "active",
                        }
                    ],
                },
            ],
        )

        mock_collection.bulk_write.assert_called_once_with(
            [
                UpdateOne(
                    {"_id": "3ea0465206d14304aa0eece4f8e1a2a4", "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "contractChangeRationaleTypes": RATIONALE_TYPES,
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [],
                                        "rev": None,
                                        "date": "2024-11-12T16:02:59.403731+02:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/contractChangeRationaleTypes"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                            }
                        },
                        {
                            "$set": {
                                "_rev": ANY,
                            }
                        },
                    ],
                ),
                UpdateOne(
                    {"_id": "3ea0465206d14304aa0eece4f8e1a2a5", "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "contractChangeRationaleTypes": RATIONALE_TYPES,
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [],
                                        "rev": None,
                                        "date": "2024-11-12T16:02:59.403731+02:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/contractChangeRationaleTypes"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                            }
                        },
                        {
                            "$set": {
                                "_rev": ANY,
                            }
                        },
                    ],
                ),
                UpdateOne(
                    {"_id": "3ea0465206d14304aa0eece4f8e1a2a6", "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "contractChangeRationaleTypes": RATIONALE_TYPES_LAW_922,
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [],
                                        "rev": None,
                                        "date": "2024-11-12T16:02:59.403731+02:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/contractChangeRationaleTypes"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                            }
                        },
                        {
                            "$set": {
                                "_rev": ANY,
                            }
                        },
                    ],
                ),
                UpdateOne(
                    {"_id": "3ea0465206d14304aa0eece4f8e1a2a7", "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "contractChangeRationaleTypes": RATIONALE_TYPES_DECREE_1178,
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [],
                                        "rev": None,
                                        "date": "2024-11-12T16:02:59.403731+02:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/contractChangeRationaleTypes"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                            }
                        },
                        {
                            "$set": {
                                "_rev": ANY,
                            }
                        },
                    ],
                ),
                UpdateOne(
                    {"_id": "3ea0465206d14304aa0eece4f8e1a2a8", "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "contractChangeRationaleTypes": RATIONALE_TYPES_DECREE_1178,
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [],
                                        "rev": None,
                                        "date": "2024-11-12T16:02:59.403731+02:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/contractChangeRationaleTypes"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                            }
                        },
                        {
                            "$set": {
                                "_rev": ANY,
                            }
                        },
                    ],
                ),
                UpdateOne(
                    {"_id": "3ea0465206d14304aa0eece4f8e1a2a9", "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "contractChangeRationaleTypes": RATIONALE_TYPES_LAW_922,
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [],
                                        "rev": None,
                                        "date": "2024-11-12T16:02:59.403731+02:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/contractChangeRationaleTypes"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                            }
                        },
                        {
                            "$set": {
                                "_rev": ANY,
                            }
                        },
                    ],
                ),
            ]
        )


if __name__ == "__main__":
    migrate_collection(Migration)
