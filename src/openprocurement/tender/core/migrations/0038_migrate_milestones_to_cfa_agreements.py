import logging
from unittest.mock import ANY, MagicMock, call, patch

from pymongo import UpdateOne

from openprocurement.api.migrations.base import (
    PymongoCollectionMigration,
    ReadonlyCollectionWrapper,
    migrate_collection,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(PymongoCollectionMigration):
    description = "Migrate milestones to agreement for closeFrameworkAgreementUA/closeFrameworkAgreementSelectionUA"

    collection_name = "tenders"

    append_revision = True

    update_date_modified: bool = True
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    def _get_agreements_collection(self):
        return ReadonlyCollectionWrapper(getattr(self.env["registry"].mongodb, "agreements").collection)

    @property
    def _agreements_collection(self):
        return self._get_agreements_collection()

    def _get_agreement_milestones(self, _id, tender):
        if agreement := self._agreements_collection.find_one({"_id": _id}, {"milestones": 1}):
            return agreement.get("milestones")
        else:
            # if agreement was not activated (created in agreements collection) yet - copy milestones from tender
            return tender.get("milestones")

    def get_filter(self):
        return {
            "agreements": {"$elemMatch": {"status": {"$in": ["pending", "active"]}, "milestones": {"$exists": False}}},
            "status": {"$nin": ["complete", "cancelled", "unsuccessful", "draft.unsuccessful"]},
            "procurementMethodType": {"$in": ["closeFrameworkAgreementUA", "closeFrameworkAgreementSelectionUA"]},
        }

    def get_projection(self) -> dict:
        return {"agreements": 1, "milestones": 1}

    def update_document(self, doc, context=None):
        for agreement in doc.get("agreements", []):
            # if agreement pending/active then copy milestones
            if agreement.get("status") and agreement["status"] in ["pending", "active"]:
                if agreement_id := agreement.get("id"):
                    if milestones := self._get_agreement_milestones(agreement_id, doc):
                        agreement["milestones"] = milestones
        return doc

    def run_test(self):
        tender_1_id = "3ea0465206d14304aa0eece4f8e1a2a4"
        tender_2_id = "5b20cae130a3465abe4e09d7d7cd2e39"
        tender_3_id = "3d87690ac08c43049452db8f89ef6811"
        tender_4_id = "3ac87bc797684169bb165177a6a08e31"
        tender_5_id = "65248827293c45cfa004be83175b6584"

        agreement_1_id = "a48fdc49cfed438fbb2880b287178ced"
        agreement_2_id = "541456190016476a8e62164bd3593980"
        agreement_3_id = "50de2cd1e67c4c2b974b6b2fd3efa299"
        agreement_4_id = "4872bd7a9b7748ffb95a4a49ef4e5a95"
        agreement_5_id = "84d39bfc15004810a5972a325c435748"
        agreement_6_id = "ac5685721ea04aaf9ecd943f8974c120"

        milestone_ids = ["73b2fca63f4c443c81bd1f6b22d4ad56", "fcd587e058db477f804f48a0001db286"]

        tenders = [
            # agreement data was not copied yet
            {
                "_id": tender_1_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "agreements": [{"id": agreement_1_id}],
            },
            # agreement data copied, milestones were not set
            {
                "_id": tender_2_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "agreements": [{"id": agreement_2_id, "status": "active"}],
            },
            # agreement data copied, milestones were not set, agreement has no milestones
            {
                "_id": tender_3_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "agreements": [{"id": agreement_3_id, "status": "active"}],
            },
            # agreement data copied, milestones not set, agreement was not created yet -> copy milestones from tender
            {
                "_id": tender_4_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "milestones": [{"id": m_id} for m_id in milestone_ids],
                "agreements": [{"id": agreement_4_id, "status": "active"}],
            },
            # agreement data copied, milestones not set, copy milestones for active agreement only
            {
                "_id": tender_5_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "agreements": [
                    {"id": agreement_5_id, "status": "active"},
                    {"id": agreement_6_id, "status": "cancelled"},
                ],
            },
        ]

        agreement_find_one_results = [
            # agreement with milestones
            {
                "_id": agreement_2_id,
                "milestones": [{"id": m_id} for m_id in milestone_ids],
            },
            # agreement with no milestones
            {
                "_id": agreement_3_id,
            },
            # agreement was not created yet
            {},
            {
                "_id": agreement_5_id,
                "milestones": [{"id": m_id} for m_id in milestone_ids],
            },
        ]

        mock_agreement_collection = MagicMock(find_one=MagicMock(side_effect=agreement_find_one_results))

        with patch.object(self, "_get_agreements_collection", return_value=mock_agreement_collection):
            mock_collection = self.run_test_data(tenders)

        assert mock_agreement_collection.find_one.call_args_list == [
            call({"_id": agreement_2_id}, {"milestones": 1}),
            call({"_id": agreement_3_id}, {"milestones": 1}),
            call({"_id": agreement_4_id}, {"milestones": 1}),
            call({"_id": agreement_5_id}, {"milestones": 1}),
        ]

        mock_collection.bulk_write.assert_called_once_with(
            [
                UpdateOne(
                    {"_id": tender_2_id, "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "_id": tender_2_id,
                                "_rev": ANY,
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/agreements/0/milestones"}],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "agreements": [
                                    {
                                        "id": agreement_2_id,
                                        "status": "active",
                                        "milestones": [{"id": m_id} for m_id in milestone_ids],
                                    }
                                ],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                        {"$set": {"dateModified": ANY}},
                        {
                            "$set": {
                                "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                                "public_ts": "$$CLUSTER_TIME",
                            }
                        },
                    ],
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
                UpdateOne(
                    {"_id": tender_4_id, "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "_id": tender_4_id,
                                "_rev": ANY,
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/agreements/0/milestones"}],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "milestones": [{"id": m_id} for m_id in milestone_ids],
                                "agreements": [
                                    {
                                        "id": agreement_4_id,
                                        "status": "active",
                                        "milestones": [{"id": m_id} for m_id in milestone_ids],
                                    }
                                ],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                        {"$set": {"dateModified": ANY}},
                        {
                            "$set": {
                                "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                                "public_ts": "$$CLUSTER_TIME",
                            }
                        },
                    ],
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
                UpdateOne(
                    {"_id": tender_5_id, "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "_id": tender_5_id,
                                "_rev": ANY,
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/agreements/0/milestones"}],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "agreements": [
                                    {
                                        "id": agreement_5_id,
                                        "status": "active",
                                        "milestones": [{"id": m_id} for m_id in milestone_ids],
                                    },
                                    {
                                        "id": agreement_6_id,
                                        "status": "cancelled",
                                    },
                                ],
                            }
                        },
                        {"$set": {"_rev": ANY}},
                        {"$set": {"dateModified": ANY}},
                        {
                            "$set": {
                                "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                                "public_ts": "$$CLUSTER_TIME",
                            }
                        },
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
    # python src/openprocurement/tender/core/migrations/0038_migrate_milestones_to_cfa_agreements.py -p <path to service.ini>
    migrate_collection(Migration)
