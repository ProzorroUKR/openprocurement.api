import json
import logging
from datetime import datetime
from unittest.mock import ANY

from pymongo import UpdateOne
from pyramid.csrf import urlparse

from openprocurement.api.constants import TZ
from openprocurement.api.context import set_request_now
from openprocurement.api.migrations.base import (
    CollectionMigration,
    CollectionMigrationArgumentParser,
    migrate_collection,
)
from openprocurement.tender.core.procedure.models.document import PostComplaintDocument

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrate tenders complaint posts with documents"

    collection_name = "tenders"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def run(self):
        self.load_raw_documents()
        self.convert_raw_documents()
        super().run()

    def load_raw_documents(self):  # pylint: disable=method-hidden
        self.documents_raw_data = {}

        documents_path = getattr(self.args, "documents_source_path", None)

        if not documents_path:
            logger.error("Documents source path is required. Use --documents-source-path argument")
            raise ValueError("--documents-source-path is required")

        with open(documents_path, "r", encoding="utf-8") as f:
            self.documents_raw_data = json.load(f)

    def convert_raw_documents(self):
        self.documents_data = {}

        for doc in self.documents_raw_data:
            complaint_id = doc["complaint_id"]
            if complaint_id:
                if complaint_id not in self.documents_data:
                    self.documents_data[complaint_id] = []

                doc_json = doc["json"]
                transformed_doc = {
                    "url": doc_json["url"],
                    "hash": doc_json["hash"],
                    "title": doc_json["title"],
                    "format": doc_json["format"],
                    "datePublished": self.convert_date(doc["created_at"]),
                    "dateModified": self.convert_date(doc["updated_at"]),
                }
                self.documents_data[complaint_id].append(transformed_doc)

    def get_filter(self):
        return {
            "$or": [
                {"complaints": {"$exists": True}},
                {"qualifications.complaints": {"$exists": True}},
                {"awards.complaints": {"$exists": True}},
            ]
        }

    def get_projection(self) -> dict:
        return {
            "complaints": 1,
            "qualifications": 1,
            "awards": 1,
            "procurementMethodType": 1,
        }

    def update_document(self, doc, context=None):
        procurement_method_type = doc.get("procurementMethodType", "")

        if "complaints" in doc:
            self.process_complaints_list(doc["complaints"], doc, procurement_method_type)

        if "qualifications" in doc:
            for qualification in doc["qualifications"]:
                if isinstance(qualification, dict) and "complaints" in qualification:
                    qualification_id = qualification.get("id")
                    self.process_complaints_list(
                        qualification["complaints"],
                        doc,
                        procurement_method_type,
                        qualification_id=qualification_id,
                    )

        if "awards" in doc:
            for award in doc["awards"]:
                if isinstance(award, dict) and "complaints" in award:
                    award_id = award.get("id")
                    self.process_complaints_list(
                        award["complaints"],
                        doc,
                        procurement_method_type,
                        award_id=award_id,
                    )

        return doc

    def process_complaints_list(self, complaints, doc, procurement_method_type, qualification_id=None, award_id=None):
        """Process a list of complaints and add documents to them"""
        tender_id = doc.get("_id")

        for complaint in complaints:
            if isinstance(complaint, dict):
                complaint_id = complaint.get("id")

                if complaint_id and complaint_id in self.documents_data:
                    documents = self.documents_data[complaint_id]

                    existing_keys = set()
                    if "documents" in complaint:
                        for existing_doc in complaint["documents"]:
                            if isinstance(existing_doc, dict) and "url" in existing_doc:
                                url_parts = existing_doc["url"].split("download=")
                                if len(url_parts) > 1:
                                    existing_keys.add(url_parts[1])

                    for index, document in enumerate(documents):
                        key = urlparse(document["url"]).path.split("/")[-1]

                        if key in existing_keys:
                            logger.info(
                                f"Document already exists with key {key} in tender {tender_id}"
                                + (
                                    (qualification_id and f" qualification {qualification_id}")
                                    or (award_id and f" award {award_id}")
                                    or ""
                                )
                            )
                            continue

                        documents[index] = self.fill_document(
                            document,
                            doc,
                            complaint,
                            procurement_method_type,
                            qualification_id=qualification_id,
                            award_id=award_id,
                        )

                        if "documents" not in complaint:
                            complaint["documents"] = []

                        complaint["documents"].append(documents[index])

                        logger.info(
                            f"Document added with key {key} in tender {tender_id}"
                            + (
                                (qualification_id and f" qualification {qualification_id}")
                                or (award_id and f" award {award_id}")
                                or ""
                            )
                        )

    def fill_document(self, document, doc, complaint, procurement_method_type, qualification_id=None, award_id=None):
        set_request_now()

        key = urlparse(document["url"]).path.split("/")[-1]

        post_document_obj = PostComplaintDocument(document)
        post_document = post_document_obj.serialize()

        post_document["dateModified"] = document["dateModified"]
        post_document["datePublished"] = document["datePublished"]

        if qualification_id:
            post_document["url"] = (
                f"/tenders/{doc['_id']}"
                f"/qualifications/{qualification_id}"
                f"/complaints/{complaint['id']}"
                f"/documents/{post_document['id']}"
                f"?download={key}"
            )
        elif award_id:
            post_document["url"] = (
                f"/tenders/{doc['_id']}"
                f"/awards/{award_id}"
                f"/complaints/{complaint['id']}"
                f"/documents/{post_document['id']}"
                f"?download={key}"
            )
        else:
            post_document["url"] = (
                f"/tenders/{doc['_id']}"
                f"/complaints/{complaint['id']}"
                f"/documents/{post_document['id']}"
                f"?download={key}"
            )

        if procurement_method_type == "belowThreshold":
            post_document["author"] = "reviewers"
        else:
            post_document["author"] = "aboveThresholdReviewers"

        return post_document

    def convert_date(self, date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        if not date.tzinfo:
            date = TZ.localize(date)
        return date.isoformat()

    def run_test(self):
        self.load_raw_documents = lambda: None  # pylint: disable=method-hidden

        self.documents_raw_data = [
            {
                "complaint_id": "8bd9e3d73b8340ba949b1f6214126914",
                "json": {
                    "url": "https://public.docs.openprocurement.org/get/a93173c8d9b44f46848371dfaac31797?KeyID=2a446ee0&Signature=PfjMLUR1Bf%2FKNNb24ErqZ9mIOnQuTFrS4ufCp3dXg4Gv5SRWc9MDjFATVtv4PbxSu1pbvaZ5okC11qNrAkr6CQ%253D%253D",
                    "hash": "md5:3c4d96ac512c512cd1c3d0165681e49f",
                    "title": "рішення вд 01.06.2020№10738+лист замовнику.pdf",
                    "format": "application/pdf",
                },
                "created_at": "2020-05-28 18:38:21",
                "updated_at": "2020-06-09 16:42:39",
            },
            {
                "complaint_id": "95c62cc027c4405d89abaf1702dde32b",
                "json": {
                    "url": "https://public.docs.openprocurement.org/get/e3c47ac9552342c1b452772ba82d7b33?KeyID=2a446ee0&Signature=5lzoyfP69z9CPifBroLx1hUxZ234Qotchw3EhawG6AIXHyvzK5SQ5O7qh0FsdDsy2DAZy47x286uf89zdqavCQ%253D%253D",
                    "hash": "md5:483430c010bcfe645a4fde690539365e",
                    "title": "рішення від 28.05.2020 № 10522.pdf",
                    "format": "application/pdf",
                },
                "created_at": "2020-05-28 18:38:21",
                "updated_at": "2020-06-09 16:42:39",
            },
            {
                "complaint_id": "007230d6141345fb9043f53f3be6c928",
                "json": {
                    "url": "https://public.docs.openprocurement.org/get/820cce445ea94afe8c69f218049110b2?KeyID=2a446ee0&Signature=qj%252BdlN1KXO7ZQLqf0t2AoegjoutkuS901GZ2AuKE977kyx4VMO4LcgNu2jaEPjsT93rl2MAbKdj%252B%252BAb9ZR8qBg%253D%253D",
                    "hash": "md5:6eb11457132f76be1119ca4b153430c0",
                    "title": "Рішення від 14.01.2020 №753.pdf",
                    "format": "application/pdf",
                },
                "created_at": "2020-01-15 17:21:59",
                "updated_at": "2020-06-09 16:44:17",
            },
            {
                "complaint_id": "e1c083ec6fe1409984bb0b275fd8b365",
                "json": {
                    "url": "https://public.docs.openprocurement.org/get/71f4e6106b544a339a63b979a6087def?KeyID=2a446ee0&Signature=AV%252BzEpmrHN%252BhDq7JOItVnnqItfjGYXHN7ZnncPvgGfRG9HOpskX4MzhjJqYbeY%2FmJ0AYfGisTJ94gfK1F6aSBw%253D%253D",
                    "hash": "md5:751fb2308010fdb41879e944d7e65cd5",
                    "title": "рішення від 26.12.2019 №19314.pdf",
                    "format": "application/pdf",
                },
                "created_at": "2019-12-26 17:41:08",
                "updated_at": "2020-06-09 16:44:17",
            },
            {
                "complaint_id": "95c62cc027c4405d89abaf1702dde32b",
                "json": {
                    "url": "https://public.docs.openprocurement.org/get/8f27273968fa4705bef5d732dc7b31ad?KeyID=2a446ee0&Signature=nBIXqUIwkzKiob8jCpN7GhuLU9m2imFePajyq4vRd01ybFPK3o194qeSZaPg4MsXYZTVf49h2SFsQlFMfocJDA%253D%253D",
                    "hash": "md5:8b651030203fcf2373e1ab16926743ad",
                    "title": "рішення від 18.05.2020 № 9540.pdf",
                    "format": "application/pdf",
                },
                "created_at": "2020-05-18 18:16:47",
                "updated_at": "2020-06-09 16:42:41",
            },
        ]

        mock_collection = self.run_test_data(
            [
                {
                    "_id": "39e5353444754b2fbe42bf0282ac951d",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    "procurementMethodType": "belowThreshold",
                    "revisions": [
                        {
                            "author": "test",
                            "changes": [],
                            "date": "2024-01-01T00:00:00.000000+02:00",
                            "rev": "1-b2e0f794769c490bacdb8053df816d10",
                        }
                    ],
                    "complaints": [
                        {
                            "id": "8bd9e3d73b8340ba949b1f6214126914",
                        }
                    ],
                    "qualifications": [
                        {
                            "id": "483d0d588cd643f69174b6ab61e49891",
                            "complaints": [
                                {
                                    "id": "007230d6141345fb9043f53f3be6c928",
                                }
                            ],
                        }
                    ],
                },
                {
                    "_id": "2ae66bda17f640e490b68cf6180609fd",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    "procurementMethodType": "aboveThresholdUA",
                    "revisions": [
                        {
                            "author": "test",
                            "changes": [],
                            "date": "2024-01-01T00:00:00.000000+02:00",
                            "rev": "1-b2e0f794769c490bacdb8053df816d10",
                        }
                    ],
                    "complaints": [
                        {
                            "id": "95c62cc027c4405d89abaf1702dde32b",
                            "documents": [
                                {
                                    "confidentiality": "public",
                                    "id": "a82d1c4958c8435f955344fa3b7b4872",
                                    "datePublished": "2024-12-16T15:16:21.690739+02:00",
                                    "hash": "md5:0019d23bef56a136a1891211d7007f6f",
                                    "title": "existing_document.pdf",
                                    "format": "application/pdf",
                                    "url": "/tenders/2ae66bda17f640e490b68cf6180609fd/complaints/95c62cc027c4405d89abaf1702dde32b/documents/a82d1c4958c8435f955344fa3b7b4872?download=8f27273968fa4705bef5d732dc7b31ad",
                                    "documentOf": "tender",
                                    "dateModified": "2024-12-16T15:16:21.690739+02:00",
                                    "author": "complaint_owner",
                                    "language": "uk",
                                }
                            ],
                        }
                    ],
                    "awards": [
                        {
                            "id": "9e0c4ece9fb44d0bb2d540b9939f87dc",
                            "complaints": [
                                {
                                    "id": "e1c083ec6fe1409984bb0b275fd8b365",
                                }
                            ],
                        }
                    ],
                },
            ],
        )

        expected_document_below_threshold = {
            "confidentiality": "public",
            "id": ANY,
            "datePublished": "2020-05-28T18:38:21+03:00",
            "hash": "md5:3c4d96ac512c512cd1c3d0165681e49f",
            "title": "рішення вд 01.06.2020№10738+лист замовнику.pdf",
            "format": "application/pdf",
            "url": ANY,
            "documentOf": "tender",
            "dateModified": "2020-06-09T16:42:39+03:00",
            "author": "reviewers",
            "language": "uk",
        }

        expected_document_above_threshold = {
            "confidentiality": "public",
            "id": ANY,
            "datePublished": "2020-05-28T18:38:21+03:00",
            "hash": "md5:483430c010bcfe645a4fde690539365e",
            "title": "рішення від 28.05.2020 № 10522.pdf",
            "format": "application/pdf",
            "url": ANY,
            "documentOf": "tender",
            "dateModified": "2020-06-09T16:42:39+03:00",
            "author": "aboveThresholdReviewers",
            "language": "uk",
        }

        expected_qualification_document = {
            "confidentiality": "public",
            "id": ANY,
            "datePublished": "2020-01-15T17:21:59+02:00",
            "hash": "md5:6eb11457132f76be1119ca4b153430c0",
            "title": "Рішення від 14.01.2020 №753.pdf",
            "format": "application/pdf",
            "url": ANY,
            "documentOf": "tender",
            "dateModified": "2020-06-09T16:44:17+03:00",
            "author": "reviewers",
            "language": "uk",
        }

        expected_award_document = {
            "confidentiality": "public",
            "id": ANY,
            "datePublished": "2019-12-26T17:41:08+02:00",
            "hash": "md5:751fb2308010fdb41879e944d7e65cd5",
            "title": "рішення від 26.12.2019 №19314.pdf",
            "format": "application/pdf",
            "url": ANY,
            "documentOf": "tender",
            "dateModified": "2020-06-09T16:44:17+03:00",
            "author": "aboveThresholdReviewers",
            "language": "uk",
        }

        expected_update_1 = UpdateOne(
            {
                "_id": "39e5353444754b2fbe42bf0282ac951d",
                "_rev": "1-b2e0f794769c490bacdb8053df816d10",
            },
            [
                {
                    "$set": {
                        "_id": "39e5353444754b2fbe42bf0282ac951d",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                        "procurementMethodType": "belowThreshold",
                        "complaints": [
                            {
                                "id": "8bd9e3d73b8340ba949b1f6214126914",
                                "documents": [
                                    expected_document_below_threshold,
                                ],
                            }
                        ],
                        "qualifications": [
                            {
                                "id": "483d0d588cd643f69174b6ab61e49891",
                                "complaints": [
                                    {
                                        "id": "007230d6141345fb9043f53f3be6c928",
                                        "documents": [
                                            expected_qualification_document,
                                        ],
                                    }
                                ],
                            }
                        ],
                        "revisions": [
                            {
                                "author": "test",
                                "changes": [],
                                "date": "2024-01-01T00:00:00.000000+02:00",
                                "rev": "1-b2e0f794769c490bacdb8053df816d10",
                            },
                            {
                                "author": "migration",
                                "changes": [
                                    {"op": "remove", "path": "/complaints/0/documents"},
                                    {"op": "remove", "path": "/qualifications/0/complaints/0/documents"},
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
        )

        expected_update_2 = UpdateOne(
            {
                "_id": "2ae66bda17f640e490b68cf6180609fd",
                "_rev": "1-b2e0f794769c490bacdb8053df816d10",
            },
            [
                {
                    "$set": {
                        "_id": "2ae66bda17f640e490b68cf6180609fd",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                        "procurementMethodType": "aboveThresholdUA",
                        "complaints": [
                            {
                                "id": "95c62cc027c4405d89abaf1702dde32b",
                                "documents": [
                                    {
                                        "confidentiality": "public",
                                        "id": "a82d1c4958c8435f955344fa3b7b4872",
                                        "datePublished": "2024-12-16T15:16:21.690739+02:00",
                                        "hash": "md5:0019d23bef56a136a1891211d7007f6f",
                                        "title": "existing_document.pdf",
                                        "format": "application/pdf",
                                        "url": "/tenders/2ae66bda17f640e490b68cf6180609fd/complaints/95c62cc027c4405d89abaf1702dde32b/documents/a82d1c4958c8435f955344fa3b7b4872?download=8f27273968fa4705bef5d732dc7b31ad",
                                        "documentOf": "tender",
                                        "dateModified": "2024-12-16T15:16:21.690739+02:00",
                                        "author": "complaint_owner",
                                        "language": "uk",
                                    },
                                    expected_document_above_threshold,
                                ],
                            }
                        ],
                        "awards": [
                            {
                                "id": "9e0c4ece9fb44d0bb2d540b9939f87dc",
                                "complaints": [
                                    {
                                        "id": "e1c083ec6fe1409984bb0b275fd8b365",
                                        "documents": [
                                            expected_award_document,
                                        ],
                                    }
                                ],
                            }
                        ],
                        "revisions": [
                            {
                                "author": "test",
                                "changes": [],
                                "date": "2024-01-01T00:00:00.000000+02:00",
                                "rev": "1-b2e0f794769c490bacdb8053df816d10",
                            },
                            {
                                "author": "migration",
                                "changes": [
                                    {"op": "remove", "path": "/complaints/0/documents/1"},
                                    {"op": "remove", "path": "/awards/0/complaints/0/documents"},
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
        )

        # Sort changes arrays for order-independent comparison
        call_args = mock_collection.bulk_write.call_args[0][0]
        expected_update_1._doc[0]["$set"]["revisions"][1]["changes"].sort(key=lambda x: x["path"])
        expected_update_2._doc[0]["$set"]["revisions"][1]["changes"].sort(key=lambda x: x["path"])
        call_args[0]._doc[0]["$set"]["revisions"][1]["changes"].sort(key=lambda x: x["path"])
        call_args[1]._doc[0]["$set"]["revisions"][1]["changes"].sort(key=lambda x: x["path"])

        mock_collection.bulk_write.assert_called_once_with([expected_update_1, expected_update_2])

        # Test URL generation
        # Extract actual documents from the call
        actual_doc_1 = call_args[0]._doc[0]["$set"]
        actual_doc_2 = call_args[1]._doc[0]["$set"]

        # Test tender-level complaint URL (belowThreshold)
        tender_complaint_doc = actual_doc_1["complaints"][0]["documents"][0]
        expected_key_1 = "a93173c8d9b44f46848371dfaac31797"
        expected_url_1 = (
            "/tenders/39e5353444754b2fbe42bf0282ac951d"
            "/complaints/8bd9e3d73b8340ba949b1f6214126914"
            f"/documents/{tender_complaint_doc['id']}"
            f"?download={expected_key_1}"
        )
        assert tender_complaint_doc["url"] == expected_url_1

        # Test qualification complaint URL
        qual_complaint_doc = actual_doc_1["qualifications"][0]["complaints"][0]["documents"][0]
        expected_key_3 = "820cce445ea94afe8c69f218049110b2"
        expected_url_3 = (
            "/tenders/39e5353444754b2fbe42bf0282ac951d"
            "/qualifications/483d0d588cd643f69174b6ab61e49891"
            "/complaints/007230d6141345fb9043f53f3be6c928"
            f"/documents/{qual_complaint_doc['id']}"
            f"?download={expected_key_3}"
        )
        assert qual_complaint_doc["url"] == expected_url_3

        # Test tender-level complaint URL (aboveThresholdUA)
        tender_complaint_doc_2 = actual_doc_2["complaints"][0]["documents"][1]  # Second document (first is existing)
        expected_key_2 = "e3c47ac9552342c1b452772ba82d7b33"
        expected_url_2 = (
            "/tenders/2ae66bda17f640e490b68cf6180609fd"
            "/complaints/95c62cc027c4405d89abaf1702dde32b"
            f"/documents/{tender_complaint_doc_2['id']}"
            f"?download={expected_key_2}"
        )
        assert tender_complaint_doc_2["url"] == expected_url_2

        # Test award complaint URL
        award_complaint_doc = actual_doc_2["awards"][0]["complaints"][0]["documents"][0]
        expected_key_4 = "71f4e6106b544a339a63b979a6087def"
        expected_url_4 = (
            "/tenders/2ae66bda17f640e490b68cf6180609fd/"
            "awards/9e0c4ece9fb44d0bb2d540b9939f87dc/"
            "complaints/e1c083ec6fe1409984bb0b275fd8b365/"
            f"documents/{award_complaint_doc['id']}"
            f"?download={expected_key_4}"
        )
        assert award_complaint_doc["url"] == expected_url_4


class MigrationArgumentParser(CollectionMigrationArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument(
            "--documents-source-path",
            help="Documents data JSON file path",
            required=False,
        )


if __name__ == "__main__":
    migrate_collection(Migration, parser=MigrationArgumentParser)
