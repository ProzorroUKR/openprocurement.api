import logging
from unittest.mock import ANY, MagicMock, call, patch

from pymongo import DESCENDING, UpdateOne

from openprocurement.api.migrations.base import (
    CollectionMigration,
    ReadonlyCollectionWrapper,
    migrate_collection,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrating milestones from tender to contract"

    collection_name = "contracts"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def process_data(self, cursor):
        cursor.sort([("public_modified", DESCENDING)])
        super().process_data(cursor)

    def get_filter(self) -> dict:
        return {"milestones": {"$exists": False}}

    def get_projection(self):
        return {"awardID": 1, "tender_id": 1}

    def _get_tenders_collection(self):
        return ReadonlyCollectionWrapper(getattr(self.env["registry"].mongodb, "tenders").collection)

    @property
    def _tenders_collection(self):
        return self._get_tenders_collection()

    def _get_tender(self, tender_id):
        return self._tenders_collection.find_one(
            {"_id": tender_id},
            {"milestones": 1, "awards.id": 1, "awards.lotID": 1},
        )

    def update_document(self, doc, context=None):
        tender = self._get_tender(doc["tender_id"])

        # iter tender.awards and find corresponding lotId using contract.awardID
        for award in tender.get("awards", []):
            if award["id"] == doc["awardID"]:
                lot_id = award.get("lotID")
                break
        else:
            lot_id = None

        # copy from tender all related lot milestones + tender related milestones, without relatedLot field
        milestones = [
            {k: v for k, v in i.items() if k not in ("relatedLot",)}
            for i in filter(lambda x: x.get("relatedLot") in (lot_id, None), tender.get("milestones", []))
        ]

        # set contract.milestones.status
        doc["milestones"] = [{**x, "status": "scheduled"} for x in milestones]

        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list:
        return [{"$set": {"milestones": doc.get("milestones", []), "revisions": doc["revisions"]}}]

    def run_test(self):
        tender_1_id = "3ea0465206d14304aa0eece4f8e1a2a4"
        award_1_id = "f67c71e5e46f4ad38ca012cda3f1bc9c"
        contract_1_id = "a48fdc49cfed438fbb2880b287178ced"
        lot_1_id = "416bcc40d78148adb420ecac24740885"
        milestones_1_ids = ["73b2fca63f4c443c81bd1f6b22d4ad56", "fcd587e058db477f804f48a0001db286"]

        tender_2_id = "5b20cae130a3465abe4e09d7d7cd2e39"
        award_2_id = "91388a66477b4cda974afff4558bb8fa"
        contract_2_id = "541456190016476a8e62164bd3593980"
        milestones_2_ids = ["f4046581d7b8430c89a065e5e64158bc", "0f15f4f3d94c4bb8aee50e28c4c2dbd7"]

        tender_3_id = "3d87690ac08c43049452db8f89ef6811"
        award_3_id = "f542f71d6fa641dab14f272d00dbaab2"
        contract_3_id = "50de2cd1e67c4c2b974b6b2fd3efa299"
        lot_3_id = "67eb06a4a9a448af871c707d7fa06163"
        milestones_3_ids = ["5e6bef99761e4b25bb52d3789b85403b", "7be05c6a56d5490cbcacb2a4b2964654"]

        contracts = [
            {
                "_id": contract_1_id,
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
                "awardID": award_1_id,
            },
            {
                "_id": contract_2_id,
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
                "awardID": award_2_id,
            },
            {
                "_id": contract_3_id,
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
                "awardID": award_3_id,
            },
        ]
        tender_find_one_results = [
            # milestones have relatedLot
            {
                "_id": tender_1_id,
                "awards": [{"id": award_1_id, "lotID": lot_1_id}],
                "milestones": [{"id": m_id, "relatedLot": lot_1_id} for m_id in milestones_1_ids],
            },
            # milestones don't have relatedLot
            {
                "_id": tender_2_id,
                "awards": [{"id": award_2_id}],
                "milestones": [{"id": m_id} for m_id in milestones_2_ids],
            },
            # milestones are mixed
            {
                "_id": tender_2_id,
                "awards": [{"id": award_3_id, "lotID": lot_3_id}],
                "milestones": [{"id": milestones_3_ids[0], "relatedLot": lot_3_id}, {"id": milestones_3_ids[1]}],
            },
        ]

        mock_tenders_collection = MagicMock(find_one=MagicMock(side_effect=tender_find_one_results))

        with patch.object(self, "_get_tenders_collection", return_value=mock_tenders_collection):
            mock_collection = self.run_test_data(contracts)

        assert mock_tenders_collection.find_one.call_args_list == [
            call({"_id": tender_1_id}, {"milestones": 1, "awards.id": 1, "awards.lotID": 1}),
            call({"_id": tender_2_id}, {"milestones": 1, "awards.id": 1, "awards.lotID": 1}),
            call({"_id": tender_3_id}, {"milestones": 1, "awards.id": 1, "awards.lotID": 1}),
        ]

        mock_collection.bulk_write.assert_called_once_with(
            [
                # copies milestone.relatedLot == award.lotID
                UpdateOne(
                    {"_id": contract_1_id, "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/milestones"}],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "milestones": [{"id": m_id, "status": "scheduled"} for m_id in milestones_1_ids],
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
                # copies milestone.relatedLot == None
                UpdateOne(
                    {"_id": contract_2_id, "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/milestones"}],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "milestones": [{"id": m_id, "status": "scheduled"} for m_id in milestones_2_ids],
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
                # copies milestone.relatedLot == award.lotID  + milestone.relatedLot == None
                UpdateOne(
                    {"_id": contract_3_id, "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/milestones"}],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "milestones": [{"id": m_id, "status": "scheduled"} for m_id in milestones_3_ids],
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
