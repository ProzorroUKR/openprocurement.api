import logging
from copy import deepcopy
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
)
from openprocurement.tender.limited.procedure.serializers.tender import (
    convert_cause_to_cause_details,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrate limited tenders causes"

    collection_name = "tenders"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {
            "procurementMethodType": {"$in": [REPORTING, NEGOTIATION, NEGOTIATION_QUICK]},
            "cause": {"$exists": True},
            "causeDetails": {"$exists": False},
        }

    def get_projection(self) -> dict:
        return {"procurementMethodType": 1, "cause": 1, "causeDescription": 1, "causeDescription_en": 1}

    def update_document(self, doc, context=None):
        prev_doc = deepcopy(doc)
        doc = convert_cause_to_cause_details(doc)

        if prev_doc != doc:
            return doc

        logger.info(f"Tender {doc['_id']}: Cause with title {doc['cause']} wasn't found in dictionary")

        return None

    def run_test(self):
        mock_collection = self.run_test_data(
            [
                {
                    "_id": "39e5353444754b2fbe42bf0282ac9510",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    "cause": "technicalReasons",
                    "causeDescription": "причина",
                    "causeDescription_en": "cause",
                    "procurementMethodType": "negotiation",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/causeDescription"}],
                            "rev": None,
                            "date": "2025-04-23T20:01:57.079339+03:00",
                        },
                    ],
                },
                {
                    "_id": "39e5353444754b2fbe42bf0282ac9511",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d11",
                    "cause": "lastHope",
                    "causeDescription": "причина",
                    "procurementMethodType": "negotiation.quick",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/causeDescription"}],
                            "rev": None,
                            "date": "2025-04-23T20:01:57.079339+03:00",
                        },
                    ],
                },
                {
                    "_id": "39e5353444754b2fbe42bf0282ac9512",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d12",
                    "cause": "hematopoieticStemCells",
                    "procurementMethodType": "reporting",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/causeDescription"}],
                            "rev": None,
                            "date": "2025-04-23T20:01:57.079339+03:00",
                        },
                    ],
                },
                {
                    "_id": "39e5353444754b2fbe42bf0282ac9513",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d13",
                    "cause": "defenceVehicles",
                    "causeDescription": "причина",
                    "procurementMethodType": "reporting",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/causeDescription"}],
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
                        "_id": "39e5353444754b2fbe42bf0282ac9510",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9510",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                                "cause": "technicalReasons",
                                "causeDescription": "причина",
                                "causeDescription_en": "cause",
                                "procurementMethodType": "negotiation",
                                "causeDetails": {
                                    "title": "technicalReasons",
                                    "scheme": "LAW922",
                                    "description": "причина",
                                    "description_en": "cause",
                                },
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/causeDescription"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/causeDetails"}],
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
                UpdateOne(
                    {
                        "_id": "39e5353444754b2fbe42bf0282ac9511",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d11",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9511",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d11",
                                "cause": "lastHope",
                                "causeDescription": "причина",
                                "procurementMethodType": "negotiation.quick",
                                "causeDetails": {
                                    "title": "lastHope",
                                    "scheme": "LAW922",
                                    "description": "причина",
                                },
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/causeDescription"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/causeDetails"}],
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
                UpdateOne(
                    {
                        "_id": "39e5353444754b2fbe42bf0282ac9512",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d12",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9512",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d12",
                                "cause": "hematopoieticStemCells",
                                "procurementMethodType": "reporting",
                                "causeDetails": {
                                    "title": "hematopoieticStemCells",
                                    "scheme": "LAW922",
                                },
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/causeDescription"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/causeDetails"}],
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
                UpdateOne(
                    {
                        "_id": "39e5353444754b2fbe42bf0282ac9513",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d13",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9513",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d13",
                                "cause": "defenceVehicles",
                                "causeDescription": "причина",
                                "procurementMethodType": "reporting",
                                "causeDetails": {
                                    "title": "defenceVehicles",
                                    "scheme": "DECREE1178",
                                    "description": "причина",
                                },
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/causeDescription"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [{"op": "remove", "path": "/causeDetails"}],
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
