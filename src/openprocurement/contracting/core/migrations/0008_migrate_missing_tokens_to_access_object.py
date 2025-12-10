import logging
from unittest.mock import ANY

from pymongo import DESCENDING, UpdateOne

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection
from openprocurement.contracting.core.procedure.models.access import AccessRole

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrating missing tender/bid contracts tokens to access object"

    collection_name = "contracts"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def process_data(self, cursor):
        cursor.sort([("public_modified", DESCENDING)])
        super().process_data(cursor)

    def get_filter(self):
        return {
            "$or": [
                {
                    "$and": [
                        {"tender_token": {"$exists": True}},
                        {"access": {"$exists": True}},
                        {"access": {"$not": {"$elemMatch": {"role": "tender"}}}},
                    ]
                },
                {
                    "$and": [
                        {"bid_token": {"$exists": True}},
                        {"access": {"$exists": True}},
                        {"access": {"$not": {"$elemMatch": {"role": "bid"}}}},
                    ]
                },
            ]
        }

    def get_projection(self):
        return {
            "tender_token": 1,
            "bid_token": 1,
            "bid_owner": 1,
            "owner_token": 1,
            "owner": 1,
            "access": 1,
        }

    def update_document(self, doc, context=None):
        is_updated = False
        access = doc.get("access", [])

        access_tender = next((item for item in access if item["role"] == AccessRole.TENDER), None)
        access_bid = next((item for item in access if item["role"] == AccessRole.BID), None)

        tender_token = doc.get("tender_token")
        if tender_token and not access_tender:
            access.append(
                {
                    "token": tender_token,
                    "owner": doc.get("owner"),
                    "role": AccessRole.TENDER,
                }
            )
            is_updated = True

        bid_token = doc.get("bid_token")
        if bid_token and not access_bid:
            access.append(
                {
                    "token": bid_token,
                    "owner": doc.get("bid_owner"),
                    "role": AccessRole.BID,
                }
            )
            is_updated = True

        if is_updated:
            return doc

        return None

    def generate_base_pipeline_stages(self, doc: dict) -> list:
        return [
            {
                "$set": {
                    "access": doc["access"],
                    "revisions": doc["revisions"],
                },
            },
        ]

    def run_test(self):
        mock_collection = self.run_test_data(
            [
                # Need migration
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a2a4",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "tender_token": "166edf748a5340c0aba39218903c52e1",
                    "owner_token": "3d2b73b2930c41268a6850db0c2c11c6",
                    "owner": "broker",
                    "bid_owner": "broker",
                    "bid_token": "2fb48a61d202411ea745e2b26a88e097",
                    "access": [
                        {
                            "token": "24624b74e1f4446fb189e65d8cfa4a94",
                            "owner": "broker",
                            "role": "contract",
                        }
                    ],
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                },
                # Don't need migration
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a2a4",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "tender_token": "166edf748a5340c0aba39218903c52e1",
                    "owner_token": "3d2b73b2930c41268a6850db0c2c11c6",
                    "owner": "broker",
                    "bid_owner": "broker",
                    "bid_token": "2fb48a61d202411ea745e2b26a88e097",
                    "access": [
                        {
                            "token": "24624b74e1f4446fb189e65d8cfa4a94",
                            "owner": "broker",
                            "role": "contract",
                        },
                        {
                            "token": "166edf748a5340c0aba39218903c52e1",
                            "owner": "broker",
                            "role": "tender",
                        },
                        {
                            "token": "2fb48a61d202411ea745e2b26a88e097",
                            "owner": "broker",
                            "role": "bid",
                        },
                    ],
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
                                "access": [
                                    # Already was there
                                    {
                                        "token": "24624b74e1f4446fb189e65d8cfa4a94",
                                        "owner": "broker",
                                        "role": "contract",
                                    },
                                    # Added
                                    {
                                        "token": "166edf748a5340c0aba39218903c52e1",
                                        "owner": "broker",
                                        "role": "tender",
                                    },
                                    # Added
                                    {
                                        "token": "2fb48a61d202411ea745e2b26a88e097",
                                        "owner": "broker",
                                        "role": "bid",
                                    },
                                ],
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
                                            {"op": "remove", "path": "/access/1"},
                                            {"op": "remove", "path": "/access/1"},
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
