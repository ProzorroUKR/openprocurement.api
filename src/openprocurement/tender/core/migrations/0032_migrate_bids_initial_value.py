import json
import logging
import os
from copy import deepcopy
from unittest.mock import ANY

from jsonpatch import apply_patch
from pymongo import UpdateOne

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection
from openprocurement.tender.core.procedure.utils import get_lot_value_status

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrating bids initial value"

    collection_name = "tenders"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {
            "bids": {
                "$exists": True,
                "$not": {"$size": 0},
            },
            "status": {
                # too early to have initial value
                "$ne": "active.tendering",
            },
            "procurementMethodType": {
                "$nin": [
                    # do not have value in first stages at all
                    "competitiveDialogueEU",
                    "competitiveDialogueUA",
                ]
            },
        }

    def update_document(self, doc, context=None):
        rewinded_doc = deepcopy(doc)

        def find_by_key(items, key, value):
            return next((item for item in items if item[key] == value), None)

        revisions = rewinded_doc.pop("revisions", [])
        for version, revision in reversed(list(enumerate(revisions))):

            changes = []
            for change in revision["changes"]:
                if change["path"].startswith("/bids"):
                    changes.append(change)

            if changes:
                apply_patch(rewinded_doc, changes, in_place=True)

            leave_auction_cnange = {"op": "replace", "path": "/status", "value": "active.tendering"}

            if leave_auction_cnange in revision["changes"]:
                break

        for bid in doc["bids"]:

            rewinded_bid = find_by_key(rewinded_doc["bids"], "id", bid["id"])
            if not rewinded_bid:
                continue

            rewinded_bid_status = rewinded_bid.get("status", "active")
            if rewinded_bid_status not in ["active", "pending"]:
                continue

            if "value" in rewinded_bid:
                bid["initialValue"] = rewinded_bid["value"]

            if "lotValues" in bid:
                for lot_value in bid["lotValues"]:

                    rewinded_lot_value = find_by_key(rewinded_bid["lotValues"], "relatedLot", lot_value["relatedLot"])
                    if not rewinded_lot_value:
                        continue

                    rewinded_lot_value_status = get_lot_value_status(rewinded_lot_value, rewinded_bid)
                    if rewinded_lot_value_status not in ["active", "pending"]:
                        continue

                    if "value" in rewinded_lot_value:
                        lot_value["initialValue"] = rewinded_lot_value["value"]

        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list:
        return [
            {
                "$set": {
                    "bids": doc["bids"],
                    "revisions": doc["revisions"],
                }
            },
        ]

    def run_test(self):
        test_file_path = os.path.join(os.path.dirname(__file__), "test", "0981b8f1884444988d2a54156ad69215.json")

        with open(test_file_path) as f:
            doc = json.load(f)

        mock_collection = self.run_test_data([doc])

        mock_collection.bulk_write.assert_called_once_with(
            [
                UpdateOne(
                    {
                        "_id": "0981b8f1884444988d2a54156ad69215",
                        "_rev": "36-2abf39e35d9e4587bb38b2ce6b4a19f9",
                    },
                    [
                        {
                            "$set": {
                                "bids": ANY,
                                "revisions": ANY,
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

        mock_calls = mock_collection.bulk_write.mock_calls
        operation = mock_calls[0].args[0][0]
        pipeline = operation._doc
        updated_doc = pipeline[0]["$set"]

        assert len(updated_doc["bids"]) == 2
        assert len(updated_doc["bids"][0]["lotValues"]) == 2
        assert len(updated_doc["bids"][1]["lotValues"]) == 2

        initial_value_0_0 = updated_doc["bids"][0]["lotValues"][0]["initialValue"]
        expected_initial_value_0_0 = {'amount': 500, 'currency': 'UAH', 'valueAddedTaxIncluded': True}
        assert initial_value_0_0 == expected_initial_value_0_0, initial_value_0_0

        initial_value_0_1 = updated_doc["bids"][0]["lotValues"][1]["initialValue"]
        expected_initial_value_0_1 = {'amount': 500, 'currency': 'UAH', 'valueAddedTaxIncluded': True}
        assert initial_value_0_1 == expected_initial_value_0_1, initial_value_0_1

        initial_value_1_0 = updated_doc["bids"][1]["lotValues"][0]["initialValue"]
        expected_initial_value_1_0 = {'amount': 500, 'currency': 'UAH', 'valueAddedTaxIncluded': True}
        assert initial_value_1_0 == expected_initial_value_1_0, initial_value_1_0

        initial_value_1_1 = updated_doc["bids"][1]["lotValues"][1]["initialValue"]
        expected_initial_value_1_1 = {'amount': 500, 'currency': 'UAH', 'valueAddedTaxIncluded': True}
        assert initial_value_1_1 == expected_initial_value_1_1, initial_value_1_1

        assert updated_doc["revisions"][-1] == {
            "author": "migration",
            "changes": [
                {"op": "remove", "path": "/bids/0/lotValues/0/initialValue"},
                {"op": "remove", "path": "/bids/0/lotValues/1/initialValue"},
                {"op": "remove", "path": "/bids/1/lotValues/0/initialValue"},
                {"op": "remove", "path": "/bids/1/lotValues/1/initialValue"},
            ],
            "rev": ANY,
            "date": ANY,
        }


if __name__ == "__main__":
    migrate_collection(Migration)
