import logging
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.constants import RATIONALE_TYPES
from openprocurement.api.migrations.base import CollectionMigration, migrate_collection

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


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

    def update_document(self, doc, context=None):
        doc["contractChangeRationaleTypes"] = RATIONALE_TYPES
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
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
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
                )
            ]
        )


if __name__ == "__main__":
    migrate_collection(Migration)
