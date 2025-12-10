import logging

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection
from openprocurement.contracting.core.procedure.models.access import AccessRole

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Remove contracts excessive token fields"

    collection_name = "contracts"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {
            "$or": [
                {"tender_token": {"$exists": True}},
                {"bid_token": {"$exists": True}},
                {"bid_owner": {"$exists": True}},
                {"owner_token": {"$exists": True}},
            ]
        }

    def get_projection(self):
        return {"tender_token": 1, "bid_token": 1, "bid_owner": 1, "owner_token": 1}

    def update_document(self, doc, context=None):
        for field_name in ("tender_token", "bid_token", "bid_owner", "owner_token"):
            doc.pop(field_name, None)
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list:
        return [
            {
                "$set": {
                    "revisions": doc["revisions"],
                },
            },
            {"$unset": ["tender_token", "bid_token", "bid_owner", "owner_token"]},
        ]

    def run_test(self):
        self.run_test_data(
            [
                # contract with `tender_token` field
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a2a4",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "public_ts": {"$timestamp": {"t": 1731431223, "i": 1}},
                    "awardID": "554892199c334a1ca1c3cb0f83453787",
                    "contractID": "UA-2024-11-12-000006-a-a1",
                    "contractNumber": "11",
                    "dateSigned": "2024-11-12T16:13:59.403731+02:00",
                    "dateModified": "2024-11-12T19:07:04.310685+02:00",
                    "dateCreated": "2024-11-12T16:02:59.403731+02:00",
                    "tender_token": "166edf748a5340c0aba39218903c52e1",
                    "tender_id": "ad01c72006d24eb9b4b358c20fa40b81",
                    "transfer_token": "e2403476288b4038b55324b319728581",
                    "owner": "broker",
                    "period": {
                        "startDate": "2024-10-14T16:55:00.114706+02:00",
                        "endDate": "2024-12-26T20:38:10.371877+02:00",
                    },
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [
                                {"op": "remove", "path": "/bid_owner"},
                                {"op": "remove", "path": "/buyer"},
                                {"op": "remove", "path": "/owner_token"},
                                {"op": "remove", "path": "/tender_id"},
                                {"op": "remove", "path": "/items"},
                                {"op": "remove", "path": "/config"},
                                {"op": "remove", "path": "/suppliers"},
                                {"op": "remove", "path": "/contractID"},
                                {"op": "remove", "path": "/value"},
                                {"op": "remove", "path": "/tender_token"},
                                {"op": "remove", "path": "/awardID"},
                                {"op": "remove", "path": "/id"},
                                {"op": "remove", "path": "/bid_token"},
                                {"op": "remove", "path": "/transfer_token"},
                                {"op": "remove", "path": "/_id"},
                                {"op": "remove", "path": "/status"},
                                {"op": "remove", "path": "/owner"},
                            ],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                    "access": [
                        {
                            "token": "2fb48a61d202411ea745e2b26a88e097",
                            "owner": "broker",
                            "role": AccessRole.BID,
                        },
                        {
                            "token": "166edf748a5340c0aba39218903c52e1",
                            "owner": "broker",
                            "role": AccessRole.TENDER,
                        },
                    ],
                },
                # contract with `bid_token` and `bid_owner` fields
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a211",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "public_ts": {"$timestamp": {"t": 1731431223, "i": 1}},
                    "awardID": "554892199c334a1ca1c3cb0f83453787",
                    "contractID": "UA-2024-11-12-000006-a-a1",
                    "contractNumber": "11",
                    "dateSigned": "2024-11-12T16:13:59.403731+02:00",
                    "dateModified": "2024-11-12T19:07:04.310685+02:00",
                    "dateCreated": "2024-11-12T16:02:59.403731+02:00",
                    "bid_owner": "broker",
                    "bid_token": "2fb48a61d202411ea745e2b26a88e097",
                    "tender_id": "ad01c72006d24eb9b4b358c20fa40b81",
                    "transfer_token": "e2403476288b4038b55324b319728581",
                    "owner": "broker",
                    "period": {
                        "startDate": "2024-10-14T16:55:00.114706+02:00",
                        "endDate": "2024-12-26T20:38:10.371877+02:00",
                    },
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [
                                {"op": "remove", "path": "/bid_owner"},
                                {"op": "remove", "path": "/buyer"},
                                {"op": "remove", "path": "/owner_token"},
                                {"op": "remove", "path": "/tender_id"},
                                {"op": "remove", "path": "/items"},
                                {"op": "remove", "path": "/config"},
                                {"op": "remove", "path": "/suppliers"},
                                {"op": "remove", "path": "/contractID"},
                                {"op": "remove", "path": "/value"},
                                {"op": "remove", "path": "/tender_token"},
                                {"op": "remove", "path": "/awardID"},
                                {"op": "remove", "path": "/id"},
                                {"op": "remove", "path": "/bid_token"},
                                {"op": "remove", "path": "/transfer_token"},
                                {"op": "remove", "path": "/_id"},
                                {"op": "remove", "path": "/status"},
                                {"op": "remove", "path": "/owner"},
                            ],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                    "access": [
                        {
                            "token": "2fb48a61d202411ea745e2b26a88e097",
                            "owner": "broker",
                            "role": AccessRole.BID,
                        },
                        {
                            "token": "166edf748a5340c0aba39218903c52e1",
                            "owner": "broker",
                            "role": AccessRole.TENDER,
                        },
                    ],
                },
                # contract with `owner_token` field generated after /credentials
                {
                    "_id": "3ea0465206d14304aa0eece4f8e1a222",
                    "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                    "public_modified": 1731431224.322,
                    "public_ts": {"$timestamp": {"t": 1731431223, "i": 1}},
                    "awardID": "554892199c334a1ca1c3cb0f83453787",
                    "contractID": "UA-2024-11-12-000006-a-a1",
                    "contractNumber": "11",
                    "dateSigned": "2024-11-12T16:13:59.403731+02:00",
                    "dateModified": "2024-11-12T19:07:04.310685+02:00",
                    "dateCreated": "2024-11-12T16:02:59.403731+02:00",
                    "owner_token": "3d2b73b2930c41268a6850db0c2c11c6",
                    "tender_id": "ad01c72006d24eb9b4b358c20fa40b81",
                    "transfer_token": "e2403476288b4038b55324b319728581",
                    "owner": "broker",
                    "period": {
                        "startDate": "2024-10-14T16:55:00.114706+02:00",
                        "endDate": "2024-12-26T20:38:10.371877+02:00",
                    },
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [
                                {"op": "remove", "path": "/bid_owner"},
                                {"op": "remove", "path": "/buyer"},
                                {"op": "remove", "path": "/owner_token"},
                                {"op": "remove", "path": "/tender_id"},
                                {"op": "remove", "path": "/items"},
                                {"op": "remove", "path": "/config"},
                                {"op": "remove", "path": "/suppliers"},
                                {"op": "remove", "path": "/contractID"},
                                {"op": "remove", "path": "/value"},
                                {"op": "remove", "path": "/tender_token"},
                                {"op": "remove", "path": "/awardID"},
                                {"op": "remove", "path": "/id"},
                                {"op": "remove", "path": "/bid_token"},
                                {"op": "remove", "path": "/transfer_token"},
                                {"op": "remove", "path": "/_id"},
                                {"op": "remove", "path": "/status"},
                                {"op": "remove", "path": "/owner"},
                            ],
                            "rev": None,
                            "date": "2024-11-12T16:02:59.403731+02:00",
                        }
                    ],
                    "access": [
                        {
                            "token": "2fb48a61d202411ea745e2b26a88e097",
                            "owner": "broker",
                            "role": AccessRole.BID,
                        },
                        {
                            "token": "166edf748a5340c0aba39218903c52e1",
                            "owner": "broker",
                            "role": AccessRole.TENDER,
                        },
                        {
                            "token": "3d2b73b2930c41268a6850db0c2c11c6",
                            "owner": "broker",
                            "role": AccessRole.CONTRACT,
                        },
                    ],
                },
            ],
        )


if __name__ == "__main__":
    migrate_collection(Migration)
