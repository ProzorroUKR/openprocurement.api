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
    description = "Migrate cfaua agreements to have milestones"

    collection_name = "agreements"

    append_revision = True

    update_date_modified: bool = True
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    def _get_tenders_collection(self):
        return ReadonlyCollectionWrapper(self.db_store.database.get_collection("tenders"))

    @property
    def _tenders_collection(self):
        return self._get_tenders_collection()

    def _get_tender_milestones(self, _id):
        if tender := self._tenders_collection.find_one({"_id": _id}, {"milestones": 1}):
            return tender.get("milestones")

    def get_filter(self):
        return {"agreementType": "closeFrameworkAgreementUA", "status": "active", "milestones": {"$exists": False}}

    def update_document(self, doc, context=None):
        if tender_id := doc.get("tender_id"):
            if milestones := self._get_tender_milestones(tender_id):
                doc["milestones"] = milestones
        return doc

    def run_test(self):
        tender_1_id = "3ea0465206d14304aa0eece4f8e1a2a4"
        agreement_1_id = "a48fdc49cfed438fbb2880b287178ced"
        milestones_1_ids = ["73b2fca63f4c443c81bd1f6b22d4ad56", "fcd587e058db477f804f48a0001db286"]

        tender_2_id = "5b20cae130a3465abe4e09d7d7cd2e39"
        agreement_2_id = "541456190016476a8e62164bd3593980"

        tender_3_id = "3d87690ac08c43049452db8f89ef6811"
        agreement_3_id = "50de2cd1e67c4c2b974b6b2fd3efa299"

        agreements = [
            {
                "_id": agreement_1_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "tender_id": tender_1_id,
            },
            {
                "_id": agreement_2_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "tender_id": tender_2_id,
            },
            {
                "_id": agreement_3_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "tender_id": tender_3_id,
            },
        ]

        tender_find_one_results = [
            # tender with milestones
            {
                "_id": tender_1_id,
                "milestones": [{"id": m_id} for m_id in milestones_1_ids],
            },
            # no milestones in tender - empty array
            {"_id": tender_2_id, "milestones": []},
            # no milestones in tender
            {
                "_id": tender_3_id,
            },
        ]

        mock_tenders_collection = MagicMock(find_one=MagicMock(side_effect=tender_find_one_results))

        with patch.object(self, "_get_tenders_collection", return_value=mock_tenders_collection):
            mock_collection = self.run_test_data(agreements)

        assert mock_tenders_collection.find_one.call_args_list == [
            call({"_id": tender_1_id}, {"milestones": 1}),
            call({"_id": tender_2_id}, {"milestones": 1}),
            call({"_id": tender_3_id}, {"milestones": 1}),
        ]

        mock_collection.bulk_write.assert_called_once_with(
            [
                UpdateOne(
                    {"_id": agreement_1_id, "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "_id": agreement_1_id,
                                "_rev": ANY,
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/milestones"}],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "tender_id": tender_1_id,
                                "milestones": [{"id": m_id} for m_id in milestones_1_ids],
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
    # python src/openprocurement/framework/core/migrations/0011_migrate_milestones_to_cfaua_agreements.py -p <path to service.ini>
    migrate_collection(Migration)
