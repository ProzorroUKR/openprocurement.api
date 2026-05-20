import logging
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.constants import PLAN_OF_UKRAINE, PLAN_OF_UKRAINE_SCHEME
from openprocurement.api.migrations.base import PymongoCollectionMigration, migrate_collection

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(PymongoCollectionMigration):
    description = "Set budget.project.scheme = plan_of_ukraine for matching plans (CS-21350)"

    collection_name = "plans"

    append_revision = True

    update_date_modified: bool = True
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self) -> dict:
        return {
            "budget.project.id": {"$in": list(PLAN_OF_UKRAINE.keys())},
            "budget.project.scheme": {"$exists": False},
        }

    def get_projection(self) -> dict:
        return {"budget": 1}

    def update_document(self, doc, context=None):
        project = (doc.get("budget") or {}).get("project") or {}
        if project.get("scheme"):
            return None
        if project.get("id") not in PLAN_OF_UKRAINE:
            return None
        project["scheme"] = PLAN_OF_UKRAINE_SCHEME
        doc["budget"]["project"] = project
        return doc

    def run_test(self):
        plan_match_id = "39e5353444754b2fbe42bf0282ac9510"
        plan_freeform_id = "39e5353444754b2fbe42bf0282ac9511"
        plan_already_scheme_id = "39e5353444754b2fbe42bf0282ac9512"

        sample_classifier_id = next(iter(PLAN_OF_UKRAINE))
        sample = PLAN_OF_UKRAINE[sample_classifier_id]

        plans = [
            {
                "_id": plan_match_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [
                    {
                        "author": "broker",
                        "changes": [],
                        "rev": None,
                        "date": "2024-11-12T16:02:59.403731+02:00",
                    }
                ],
                "budget": {
                    "project": {
                        "id": sample_classifier_id,
                        "name": sample["name_uk"],
                        "name_en": sample["name_en"],
                    },
                },
            },
            {
                "_id": plan_freeform_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [],
                "budget": {"project": {"id": "freeform-123", "name": "proj_name"}},
            },
            {
                "_id": plan_already_scheme_id,
                "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e",
                "revisions": [],
                "budget": {
                    "project": {
                        "id": sample_classifier_id,
                        "name": sample["name_uk"],
                        "scheme": PLAN_OF_UKRAINE_SCHEME,
                    }
                },
            },
        ]

        mock_collection = self.run_test_data(plans)

        mock_collection.bulk_write.assert_called_once_with(
            [
                UpdateOne(
                    {"_id": plan_match_id, "_rev": "7-5ae2fd5ee31142ad8bb203b04c434e4e"},
                    [
                        {
                            "$set": {
                                "_id": plan_match_id,
                                "_rev": ANY,
                                "revisions": [
                                    {"author": "broker", "changes": [], "rev": ANY, "date": ANY},
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/budget/project/scheme"}],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "budget": {
                                    "project": {
                                        "id": sample_classifier_id,
                                        "name": sample["name_uk"],
                                        "name_en": sample["name_en"],
                                        "scheme": PLAN_OF_UKRAINE_SCHEME,
                                    },
                                },
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
    # python src/openprocurement/api/migrations/0003_migrate_plan_budget_project_scheme.py -p <path to service.ini>
    migrate_collection(Migration)
