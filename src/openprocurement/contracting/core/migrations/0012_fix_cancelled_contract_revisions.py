import logging
from copy import deepcopy
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.migrations.base import PymongoCollectionMigration, migrate_collection
from openprocurement.api.procedure.utils import get_revision_changes

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def is_bad_contract_revision(revision):
    changes = revision.get("changes", [])
    if not changes:
        return False
    if not all(change.get("op") == "remove" for change in changes):
        return False
    return any(change["path"] == "/status" for change in changes)


def build_contract_before_cancelled(contract):
    contract_before = deepcopy(contract)
    contract_before["status"] = "pending"
    contract_before["date"] = contract.get("dateCreated") or contract["revisions"][0]["date"]
    for cancellation in contract_before.get("cancellations", []):
        if cancellation.get("status") == "active" and cancellation.get("reasonType") == "signingRefusal":
            cancellation["status"] = "pending"
    return contract_before


class Migration(PymongoCollectionMigration):
    description = "Fix eContract cancellation revisions saved with empty contract_src"

    collection_name = "contracts"

    append_revision = False
    update_date_modified = False
    update_feed_position = False

    log_every = 100000
    bulk_max_size = 500

    def get_filter(self):
        return {
            "status": "cancelled",
            "buyer.contract_owner": {"$exists": True},
            "revisions.1": {"$exists": True},
        }

    def update_document(self, doc, context=None):
        revisions = doc.get("revisions", [])
        if len(revisions) < 2:
            return None

        last_revision = revisions[-1]
        if not is_bad_contract_revision(last_revision):
            return None

        contract_before = build_contract_before_cancelled(doc)
        correct_changes = get_revision_changes(doc, contract_before)
        if not correct_changes:
            return None

        if last_revision["changes"] == correct_changes:
            return None

        last_revision["changes"] = correct_changes
        logger.info("Fixed cancellation revision for contract %s", doc["_id"])
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list:
        return [
            {
                "$set": {
                    "revisions": doc["revisions"],
                }
            },
        ]

    def run_test(self):
        contract_id = "03f2a22dfb8a4f1abefa11240c950406"
        contract = {
            "_id": contract_id,
            "_rev": "3-885ad5d09ba447d2a59b89a95176d16e",
            "status": "cancelled",
            "date": "2026-08-21T01:24:02.310881+03:00",
            "dateCreated": "2026-08-21T01:23:58.887475+03:00",
            "title": "Lot title",
            "buyer": {"contract_owner": "broker"},
            "revisions": [
                {
                    "author": "broker",
                    "changes": get_revision_changes({"status": "pending", "title": "Lot title"}, {}),
                    "rev": None,
                    "date": "2026-08-21T01:23:58.887475+03:00",
                },
                {
                    "author": "broker",
                    "changes": get_revision_changes(
                        {
                            "status": "cancelled",
                            "date": "2026-08-21T01:24:02.310881+03:00",
                            "title": "Lot title",
                            "buyer": {"contract_owner": "broker"},
                        },
                        {},
                    ),
                    "rev": "2-db7fb4c2a4a64ffd8b29784c4e6bcc25",
                    "date": "2026-08-21T01:24:02.310881+03:00",
                },
            ],
        }
        skipped_contract = {
            "_id": "already-fixed",
            "_rev": "2-x",
            "status": "cancelled",
            "date": "2026-08-21T01:24:02.310881+03:00",
            "dateCreated": "2026-08-21T01:23:58.887475+03:00",
            "buyer": {"contract_owner": "broker"},
            "revisions": [
                {"author": "broker", "changes": [], "rev": None, "date": "2026-08-21T01:23:58.887475+03:00"},
                {
                    "author": "broker",
                    "changes": get_revision_changes(
                        {
                            "status": "cancelled",
                            "date": "2026-08-21T01:24:02.310881+03:00",
                        },
                        {
                            "status": "pending",
                            "date": "2026-08-21T01:23:58.887475+03:00",
                        },
                    ),
                    "rev": "2-x",
                    "date": "2026-08-21T01:24:02.310881+03:00",
                },
            ],
        }

        mock_collection = self.run_test_data([contract, skipped_contract])

        fixed_contract = deepcopy(contract)
        fixed_contract["revisions"][-1]["changes"] = get_revision_changes(
            fixed_contract,
            build_contract_before_cancelled(fixed_contract),
        )

        mock_collection.bulk_write.assert_called_once_with(
            [
                UpdateOne(
                    {"_id": contract_id, "_rev": "3-885ad5d09ba447d2a59b89a95176d16e"},
                    [
                        {
                            "$set": {
                                "revisions": fixed_contract["revisions"],
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
