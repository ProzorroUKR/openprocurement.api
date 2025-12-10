import logging
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection
from openprocurement.framework.cfaua.constants import CFA_UA

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrating agreementType from cfaua to closeFrameworkAgreementUA"

    collection_name = "agreements"

    append_revision = False

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {
            "agreementType": "cfaua",
        }

    def get_projection(self) -> dict:
        return {
            "agreementType": 1,
        }

    def update_document(self, doc, context=None):
        if doc["agreementType"] == "cfaua":
            doc["agreementType"] = "closeFrameworkAgreementUA"

            assert doc["agreementType"] == CFA_UA

        return doc

    def run_test(self):
        mock_collection = self.run_test_data(
            [
                {
                    "_id": "39e5353444754b2fbe42bf0282ac951d",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    "agreementType": "cfaua",
                }
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
                                "agreementType": "closeFrameworkAgreementUA",
                            }
                        },
                        {
                            "$set": {
                                "_rev": ANY,
                            }
                        },
                    ],
                )
            ]
        )


if __name__ == "__main__":
    migrate_collection(Migration)
