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
    set_cause_details_from_dictionary,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrate limited tenders causes"

    collection_name = "tenders"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {
            "procurementMethodType": {"$in": [REPORTING, NEGOTIATION, NEGOTIATION_QUICK]},
            "$or": [
                {"cause": {"$exists": True}},
                {"causeDetails": {"$exists": True}},
            ],
        }

    def get_projection(self) -> dict:
        return {
            "procurementMethodType": 1,
            "cause": 1,
            "causeDescription": 1,
            "causeDescription_en": 1,
            "causeDescription_ru": 1,
            "causeDetails": 1,
        }

    def update_document(self, doc, context=None):
        prev_doc = deepcopy(doc)
        if doc.get("causeDetails") and not doc.get("cause"):
            doc["causeDetails"]["code"] = doc["causeDetails"]["title"]
            doc = set_cause_details_from_dictionary(doc)
        else:
            doc = convert_cause_to_cause_details(doc)
            for field_name in ("cause", "causeDescription", "causeDescription_en", "causeDescription_ru"):
                doc.pop(field_name, None)

        if prev_doc != doc:
            return doc

        logger.info(f"Tender {doc['_id']}: Cause with code {doc['cause']} wasn't found in dictionary")

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
                {
                    "_id": "39e5353444754b2fbe42bf0282ac9514",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d14",
                    "cause": "defenceVehicles",
                    "causeDescription": "причина",
                    "causeDetails": {
                        "title": "defenceVehicles",
                        "scheme": "DECREE1178",
                        "description": "причина",
                    },
                    "procurementMethodType": "reporting",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/causeDetails"}],
                            "rev": None,
                            "date": "2025-04-23T20:01:57.079339+03:00",
                        },
                    ],
                },
                {
                    "_id": "39e5353444754b2fbe42bf0282ac9515",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d15",
                    "causeDetails": {
                        "title": "naturalGas",
                        "scheme": "DECREE1178",
                        "description": "причина",
                        "description_en": "naturalGas",
                    },
                    "procurementMethodType": "reporting",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/causeDetails"}],
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
                                "procurementMethodType": "negotiation",
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/causeDescription"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/causeDetails"},
                                            {"op": "add", "path": "/cause", "value": "technicalReasons"},
                                            {"op": "add", "path": "/causeDescription", "value": "причина"},
                                            {"op": "add", "path": "/causeDescription_en", "value": "cause"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "causeDetails": {
                                    "code": "technicalReasons",
                                    "description": "причина",
                                    "description_en": "cause",
                                    "scheme": "LAW922",
                                    "title": "Абзац 4 пункту 2 частини 2 статті 40",
                                    "title_en": "Paragraph 4, Clause 2, Part 2, Article 40",
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
                        "_id": "39e5353444754b2fbe42bf0282ac9511",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d11",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9511",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d11",
                                "procurementMethodType": "negotiation.quick",
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/causeDescription"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/causeDetails"},
                                            {"op": "add", "path": "/cause", "value": "lastHope"},
                                            {"op": "add", "path": "/causeDescription", "value": "причина"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "causeDetails": {
                                    "code": "lastHope",
                                    "description": "причина",
                                    "scheme": "LAW922",
                                    "title": "Абзац 6 пункту 2 частини 2 статті 40",
                                    "title_en": "Paragraph 6, subparagraph 2, paragraph 2, Article 40",
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
                        "_id": "39e5353444754b2fbe42bf0282ac9512",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d12",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9512",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d12",
                                "procurementMethodType": "reporting",
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/causeDescription"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/causeDetails"},
                                            {"op": "add", "path": "/cause", "value": "hematopoieticStemCells"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "causeDetails": {
                                    "code": "hematopoieticStemCells",
                                    "scheme": "LAW922",
                                    "title": "Пункт 21 частини 5 статті 3",
                                    "title_en": "Clause 21, Part 5, Article 3",
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
                        "_id": "39e5353444754b2fbe42bf0282ac9513",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d13",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9513",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d13",
                                "procurementMethodType": "reporting",
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/causeDescription"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/causeDetails"},
                                            {"op": "add", "path": "/cause", "value": "defenceVehicles"},
                                            {"op": "add", "path": "/causeDescription", "value": "причина"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "causeDetails": {
                                    "code": "defenceVehicles",
                                    "description": "причина",
                                    "scheme": "DECREE1178",
                                    "title": "Підпункт 24 пункту 13",
                                    "title_en": "Subparagraph 24 of paragraph 13",
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
                        "_id": "39e5353444754b2fbe42bf0282ac9514",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d14",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9514",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d14",
                                "procurementMethodType": "reporting",
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/causeDetails"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/causeDetails/code"},
                                            {"op": "remove", "path": "/causeDetails/title_en"},
                                            {
                                                "op": "replace",
                                                "path": "/causeDetails/title",
                                                "value": "defenceVehicles",
                                            },
                                            {"op": "add", "path": "/cause", "value": "defenceVehicles"},
                                            {"op": "add", "path": "/causeDescription", "value": "причина"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "causeDetails": {
                                    "code": "defenceVehicles",
                                    "description": "причина",
                                    "scheme": "DECREE1178",
                                    "title": "Підпункт 24 пункту 13",
                                    "title_en": "Subparagraph 24 of paragraph 13",
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
                        "_id": "39e5353444754b2fbe42bf0282ac9515",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d15",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9515",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d15",
                                "procurementMethodType": "reporting",
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/causeDetails"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {"op": "remove", "path": "/causeDetails/code"},
                                            {"op": "remove", "path": "/causeDetails/title_en"},
                                            {"op": "replace", "path": "/causeDetails/title", "value": "naturalGas"},
                                        ],
                                        "rev": ANY,
                                        "date": ANY,
                                    },
                                ],
                                "causeDetails": {
                                    "code": "naturalGas",
                                    "description": "причина",
                                    "description_en": "naturalGas",
                                    "scheme": "DECREE1178",
                                    "title": "Підпункт 18 пункту 13",
                                    "title_en": "Subparagraph 18 of paragraph 13",
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
