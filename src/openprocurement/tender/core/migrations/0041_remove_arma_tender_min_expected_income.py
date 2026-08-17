import logging
from typing import Any
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.migrations.base import (
    PymongoCollectionMigration,
    migrate_collection,
)
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(PymongoCollectionMigration):
    description = "Remove tender level minExpectedIncome from complexAsset.arma tenders (moved to lot level)"

    collection_name = "tenders"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self) -> dict:
        return {
            "procurementMethodType": COMPLEX_ASSET_ARMA,
            "minExpectedIncome": {"$exists": True},
        }

    def get_projection(self) -> dict:
        return {
            "procurementMethodType": 1,
            "minExpectedIncome": 1,
        }

    def update_document(self, doc: dict, context: Any = None) -> dict | None:
        if "minExpectedIncome" not in doc:
            return None

        del doc["minExpectedIncome"]
        return doc

    def generate_base_pipeline_stages(self, doc: dict) -> list[dict]:
        unset_pipeline = [{"$unset": "minExpectedIncome"}]
        return unset_pipeline + super().generate_base_pipeline_stages(doc)

    def run_test(self) -> None:
        mock_collection = self.run_test_data(
            [
                {
                    "_id": "aaa00000000000000000000000000001",
                    "_rev": "1-aaa00000000000000000000000000001",
                    "procurementMethodType": COMPLEX_ASSET_ARMA,
                    "minExpectedIncome": {"amount": 100000.0, "currency": "UAH"},
                },
                {
                    "_id": "aaa00000000000000000000000000002",
                    "_rev": "1-aaa00000000000000000000000000002",
                    "procurementMethodType": COMPLEX_ASSET_ARMA,
                },
            ],
        )

        mock_collection.bulk_write.assert_called_once_with(
            [
                UpdateOne(
                    {
                        "_id": "aaa00000000000000000000000000001",
                        "_rev": "1-aaa00000000000000000000000000001",
                    },
                    [
                        {"$unset": "minExpectedIncome"},
                        {
                            "$set": {
                                "_id": "aaa00000000000000000000000000001",
                                "_rev": "1-aaa00000000000000000000000000001",
                                "procurementMethodType": COMPLEX_ASSET_ARMA,
                            }
                        },
                        {"$set": {"_rev": ANY}},
                    ],
                ),
            ]
        )


if __name__ == "__main__":
    migrate_collection(Migration)
