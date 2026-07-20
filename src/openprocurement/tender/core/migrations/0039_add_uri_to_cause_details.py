import logging
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.deprecated.cause_details import PROCUREMENT_METHOD_TYPE_TO_FROZEN_CAUSE_DETAILS_MAPPING_ALL
from openprocurement.api.migrations.base import PymongoCollectionMigration, migrate_collection
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
)
from openprocurement.tender.limited.procedure.serializers.cause import enrich_cause_details, get_cause_details_reference

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(PymongoCollectionMigration):
    description = "Add uri field to causeDetails for limited tenders"

    collection_name = "tenders"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {
            "procurementMethodType": {"$in": [REPORTING, NEGOTIATION, NEGOTIATION_QUICK]},
            "causeDetails": {"$exists": True},
            "causeDetails.uri": {"$exists": False},
        }

    def get_projection(self) -> dict:
        return {
            "procurementMethodType": 1,
            "causeDetails": 1,
        }

    def update_document(self, doc, context=None):
        cause_details = doc.get("causeDetails")
        mapping = PROCUREMENT_METHOD_TYPE_TO_FROZEN_CAUSE_DETAILS_MAPPING_ALL
        cause_details_reference = get_cause_details_reference(doc, mapping)
        doc["causeDetails"] = enrich_cause_details(cause_details, cause_details_reference)
        return doc

    def run_test(self):
        mock_collection = self.run_test_data(
            [
                {
                    "_id": "39e5353444754b2fbe42bf0282ac9520",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d20",
                    "procurementMethodType": "negotiation",
                    "causeDetails": {
                        "code": "technicalReasons",
                        "description": "причина",
                        "scheme": "LAW922",
                        "title": "Абзац 4 пункту 2 частини 2 статті 40",
                        "title_en": "Paragraph 4, Clause 2, Part 2, Article 40",
                    },
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "add", "path": "/causeDetails"}],
                            "rev": None,
                            "date": "2025-04-23T20:01:57.079339+03:00",
                        },
                    ],
                },
                {
                    "_id": "39e5353444754b2fbe42bf0282ac9521",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d21",
                    "procurementMethodType": "reporting",
                    "causeDetails": {
                        "code": "naturalGas",
                        "description": "причина",
                        "scheme": "DECREE1178",
                        "title": "Підпункт 18 пункту 13",
                        "title_en": "Subparagraph 18 of paragraph 13",
                    },
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "add", "path": "/causeDetails"}],
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
                        "_id": "39e5353444754b2fbe42bf0282ac9520",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d20",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9520",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d20",
                                "procurementMethodType": "negotiation",
                                "causeDetails": {
                                    "code": "technicalReasons",
                                    "description": "причина",
                                    "scheme": "LAW922",
                                    "title": "Абзац 4 пункту 2 частини 2 статті 40",
                                    "title_en": "Paragraph 4, Clause 2, Part 2, Article 40",
                                    "uri": "https://zakon.rada.gov.ua/laws/show/922-19/ed20251031#n1717",
                                },
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "add", "path": "/causeDetails"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {
                                                "op": "remove",
                                                "path": "/causeDetails/uri",
                                            },
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
                    ],
                ),
                UpdateOne(
                    {
                        "_id": "39e5353444754b2fbe42bf0282ac9521",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d21",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9521",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d21",
                                "procurementMethodType": "reporting",
                                "causeDetails": {
                                    "code": "naturalGas",
                                    "description": "причина",
                                    "scheme": "DECREE1178",
                                    "title": "Підпункт 18 пункту 13",
                                    "title_en": "Subparagraph 18 of paragraph 13",
                                    "uri": "https://zakon.rada.gov.ua/laws/show/1178-2022-%D0%BF#n426",
                                },
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "add", "path": "/causeDetails"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {
                                                "op": "remove",
                                                "path": "/causeDetails/uri",
                                            },
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
                    ],
                ),
            ]
        )


if __name__ == "__main__":
    migrate_collection(Migration)
