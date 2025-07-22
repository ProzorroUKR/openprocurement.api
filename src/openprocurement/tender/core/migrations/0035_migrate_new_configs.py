import logging
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection
from openprocurement.tender.core.procedure.serializers.config import (
    tender_config_enquiry_period_regulation_migrate_value,
    tender_config_has_enquiries_migrate_value,
    tender_config_min_enquiries_duration_migrate_value,
    tender_config_min_tendering_duration_migrate_value,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrate tender configs: minTenderingDuration"

    collection_name = "tenders"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {
            "$or": [
                {"config.minTenderingDuration": {"$exists": False}},
                {"config.hasEnquiries": {"$exists": False}},
                {"config.minEnquiriesDuration": {"$exists": False}},
                {"config.enquiryPeriodRegulation": {"$exists": False}},
            ]
        }

    def get_projection(self) -> dict:
        return {"config": 1, "procurementMethodType": 1}

    def update_document(self, doc, context=None):
        mapping = {
            "minTenderingDuration": tender_config_min_tendering_duration_migrate_value,
            "hasEnquiries": tender_config_has_enquiries_migrate_value,
            "minEnquiriesDuration": tender_config_min_enquiries_duration_migrate_value,
            "enquiryPeriodRegulation": tender_config_enquiry_period_regulation_migrate_value,
        }
        for key, migrate_value in mapping.items():
            if doc["config"].get(key) is None:
                doc["config"][key] = migrate_value(doc)
        return doc

    def run_test(self):
        mock_collection = self.run_test_data(
            [
                {
                    "_id": "39e5353444754b2fbe42bf0282ac951d",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    "procurementMethodType": "aboveThreshold",
                    "config": {
                        "hasAuction": True,
                    },
                },
                {
                    "_id": "3b2804fb60b94d6ca35192ed6baafb4c",
                    "_rev": "1-a60c88126b244e4fbeed3522268a90c7",
                    "procurementMethodType": "competitiveOrdering",
                    "config": {
                        "hasAuction": True,
                    },
                },
            ],
        )

        mock_collection.bulk_write.assert_called_once_with(
            [
                UpdateOne(
                    {
                        "_id": "39e5353444754b2fbe42bf0282ac951d",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac951d",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                                "procurementMethodType": "aboveThreshold",
                                "config": {
                                    "hasAuction": True,
                                    "minTenderingDuration": 7,
                                    "hasEnquiries": False,
                                    "minEnquiriesDuration": 0,
                                    "enquiryPeriodRegulation": 3,
                                },
                            }
                        },
                        {
                            "$set": {
                                "_rev": ANY,
                            }
                        },
                    ],
                ),
                UpdateOne(
                    {
                        "_id": "3b2804fb60b94d6ca35192ed6baafb4c",
                        "_rev": "1-a60c88126b244e4fbeed3522268a90c7",
                    },
                    [
                        {
                            "$set": {
                                "_id": "3b2804fb60b94d6ca35192ed6baafb4c",
                                "_rev": "1-a60c88126b244e4fbeed3522268a90c7",
                                "procurementMethodType": "competitiveOrdering",
                                "config": {
                                    "hasAuction": True,
                                    "minTenderingDuration": 3,
                                    "hasEnquiries": False,
                                    "minEnquiriesDuration": 0,
                                    "enquiryPeriodRegulation": 3,
                                },
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


if __name__ == "__main__":
    migrate_collection(Migration)
