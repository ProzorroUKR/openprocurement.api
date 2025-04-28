import json
import logging
import os
from copy import deepcopy

from jsonpatch import apply_patch

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
                "$size": {"$gt": 0},
            },
            "status": {"$ne": "active.tendering"},
            "procurementMethodType": {"$nin": ["competitiveDialogueEU", "competitiveDialogueUA"]},  # do not have value in first stages
        }

    def update_document(self, doc):
        def get_item(items, field, value):
            for item in items:
                if item[field] == value:
                    return item
            return None

        rewinded_doc = deepcopy(doc)

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
            rewinded_bid = get_item(rewinded_doc["bids"], "id", bid["id"])
            if rewinded_bid:
                if "value" in bid:
                    bid["initialValue"] = rewinded_bid["value"]
                if "lotValues" in bid:
                    for lot_value in bid["lotValues"]:
                        if "value" in lot_value:
                            rewinded_lot_value = get_item(
                                rewinded_bid["lotValues"], "relatedLot", lot_value["relatedLot"]
                            )
                            if rewinded_lot_value:
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

        call = mock_collection.bulk_write.mock_calls[0]
        operation = call.args[0][0]
        pipeline = operation._doc
        updated_doc = pipeline[0]["$set"]

        minimized_bids = []
        for bid in updated_doc["bids"]:
            minimized_bid = {}
            if "value" in bid:
                minimized_bid["value"] = bid["value"]
                minimized_bid["initialValue"] = bid["initialValue"]
            if "lotValues" in bid:
                minimized_bid["lotValues"] = []
                for lot_value in bid["lotValues"]:
                    if "value" in lot_value:
                        minimized_bid["lotValues"].append(
                            {
                                "value": lot_value["value"],
                                "initialValue": lot_value["initialValue"],
                                "relatedLot": lot_value["relatedLot"],
                            }
                        )
            minimized_bids.append(minimized_bid)

        logger.info(json.dumps(minimized_bids, indent=4))
        logger.info(json.dumps(updated_doc["revisions"][-1], indent=4))


if __name__ == "__main__":
    migrate_collection(Migration)
