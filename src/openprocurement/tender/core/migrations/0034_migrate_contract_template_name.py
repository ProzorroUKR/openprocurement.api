import logging
import re
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrate contract template name"

    collection_name = "tenders"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {"contractTemplateName": {"$exists": True}}

    def get_projection(self) -> dict:
        return {"contractTemplateName": 1}

    def update_document(self, doc, context=None):
        """
        Convert contract template name from old format to new format
        old format: 00000000-0.0001.01
        new format: 00000000.0001.01
        """
        contract_template_name = doc.get("contractTemplateName", "")
        old_contract_template_name_pattern = r"^\d{8}-\d\.\d{4}\.\d{2}$"
        if re.match(old_contract_template_name_pattern, contract_template_name):
            doc["contractTemplateName"] = re.sub(r"^(\d{8})-\d(\.\d{4}\.\d{2})$", r"\1\2", contract_template_name)
        return doc

    def run_test(self):
        mock_collection = self.run_test_data(
            [
                {
                    "_id": "39e5353444754b2fbe42bf0282ac951d",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    "contractTemplateName": "00000000-0.0001.01",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/contractTemplateName"}],
                            "rev": None,
                            "date": "2025-04-23T20:01:57.079339+03:00",
                        },
                    ],
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
                                "contractTemplateName": "00000000.0001.01",
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/contractTemplateName"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {
                                                "op": "replace",
                                                "path": "/contractTemplateName",
                                                "value": "00000000-0.0001.01",
                                            }
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                            }
                        },
                        {
                            "$set": {
                                "_rev": ANY,
                            }
                        },
                        {
                            "$set": {
                                "public_modified": {"$divide": [{"$toLong": "$$NOW"}, 1000]},
                                "public_ts": "$$CLUSTER_TIME",
                            }
                        },
                    ],
                ),
            ]
        )


if __name__ == "__main__":
    migrate_collection(Migration)
