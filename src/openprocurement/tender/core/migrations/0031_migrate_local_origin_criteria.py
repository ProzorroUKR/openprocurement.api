import logging

from openprocurement.api.constants import COUNTRIES_MAP
from openprocurement.api.migrations.base import CollectionMigration, migrate_collection
from openprocurement.tender.core.constants import CRITERION_LOCALIZATION
from openprocurement.tender.core.procedure.models.criterion import DataSchema

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrating tenders localization criteria"

    collection_name = "tenders"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {"criteria": {"$exists": True}}

    def get_projection(self):
        return {"criteria": 1}

    def update_document(self, doc, context=None):
        is_updated = False
        for criterion in doc["criteria"]:
            if criterion.get("classification", {}).get("id") == CRITERION_LOCALIZATION:
                for rg in criterion.get("requirementGroups", []):
                    for req in rg.get("requirements", []):
                        if req.get("expectedValues") is not None and not set(req["expectedValues"]) - set(
                            COUNTRIES_MAP.keys()
                        ):
                            req["dataSchema"] = DataSchema.ISO_3166.value
                            is_updated = True

        if is_updated:
            return doc

        return None

    def run_test(self):
        self.run_test_data(
            [
                {
                    "_id": "39e5353444754b2fbe42bf0282ac951d",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    "criteria": [
                        {
                            "classification": {"id": CRITERION_LOCALIZATION},
                            "requirementGroups": [{"requirements": [{"expectedValues": ["UA", "GB"]}]}],
                        }
                    ],
                }
            ],
        )


if __name__ == "__main__":
    migrate_collection(Migration)
