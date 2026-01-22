import logging
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrate cancellation sign documents in tender"

    collection_name = "tenders"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = False

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {"cancellations": {"$exists": True}}

    def get_projection(self) -> dict:
        return {
            "cancellations": 1,
        }

    def update_document(self, doc, context=None):
        for cancellation in doc.get("cancellations", []):
            for document in cancellation.get("documents", []):
                if document.get("title") == "sign.p7s" and document.get("format") == "application/pkcs7-signature":
                    document["documentType"] = "cancellationReport"
        return doc

    def run_test(self):
        mock_collection = self.run_test_data(
            [
                {  # tender without cancellations
                    "_id": "39e5353444754b2fbe42bf0282ac9510",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/procurementMethodType"}],
                            "rev": None,
                            "date": "2025-04-23T20:01:57.079339+03:00",
                        },
                    ],
                },
                {  # # tender without documents in cancellations
                    "_id": "39e5353444754b2fbe42bf0282ac9511",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d11",
                    "cancellations": [
                        {
                            "id": "828f56f4d3b54e3c8d3e262c80052e45",
                            "status": "pending",
                        }
                    ],
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/procurementMethodType"}],
                            "rev": None,
                            "date": "2025-04-23T20:01:57.079339+03:00",
                        },
                    ],
                },
                {  # tender without sign document in cancellation
                    "_id": "39e5353444754b2fbe42bf0282ac9512",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d12",
                    "cancellations": [
                        {
                            "id": "828f56f4d3b54e3c8d3e262c80052e45",
                            "status": "pending",
                            "documents": [
                                {
                                    "confidentiality": "public",
                                    "hash": "md5:5e1fc8654c080f2e89cc5bd2b1aa1d26",
                                    "title": "IMG_20231118_214039 (copy).jpg",
                                    "format": "image/jpeg",
                                    "url": "/tenders/15c1322a6b3e431d9129e6dbf06c9249/cancellations/828f56f4d3b54e3c8d3e262c80052e45/documents/a1bd66bef1e44248a3030d0d2b9affe1?download=893133c08cd545abb6c8dfd457d685f2",
                                    "documentOf": "tender",
                                    "language": "uk",
                                    "id": "a1bd66bef1e44248a3030d0d2b9affe1",
                                    "datePublished": "2025-08-08T16:42:21.597759+03:00",
                                    "dateModified": "2025-08-08T16:42:21.597759+03:00",
                                },
                            ],
                        }
                    ],
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/procurementMethodType"}],
                            "rev": None,
                            "date": "2025-04-23T20:01:57.079339+03:00",
                        },
                    ],
                },
                {  # tender with sign doc in cancellations
                    "_id": "39e5353444754b2fbe42bf0282ac9513",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d13",
                    "cancellations": [
                        {
                            "id": "828f56f4d3b54e3c8d3e262c80052e45",
                            "status": "pending",
                            "documents": [
                                {
                                    "confidentiality": "public",
                                    "hash": "md5:5e1fc8654c080f2e89cc5bd2b1aa1d26",
                                    "title": "IMG_20231118_214039 (copy).jpg",
                                    "format": "image/jpeg",
                                    "url": "/tenders/15c1322a6b3e431d9129e6dbf06c9249/cancellations/828f56f4d3b54e3c8d3e262c80052e45/documents/a1bd66bef1e44248a3030d0d2b9affe1?download=893133c08cd545abb6c8dfd457d685f2",
                                    "documentOf": "tender",
                                    "language": "uk",
                                    "id": "a1bd66bef1e44248a3030d0d2b9affe1",
                                    "datePublished": "2025-08-08T16:42:21.597759+03:00",
                                    "dateModified": "2025-08-08T16:42:21.597759+03:00",
                                },
                                {
                                    "confidentiality": "public",
                                    "hash": "md5:53a994d967c6bac2c6fb613190eacffc",
                                    "title": "sign.p7s",
                                    "format": "application/pkcs7-signature",
                                    "url": "/tenders/15c1322a6b3e431d9129e6dbf06c9249/cancellations/828f56f4d3b54e3c8d3e262c80052e45/documents/2c2665b1ac404065bfe8dfed7900ec9a?download=0ddec4f9dde247718ad3e841def675e2",
                                    "documentOf": "tender",
                                    "language": "uk",
                                    "id": "2c2665b1ac404065bfe8dfed7900ec9a",
                                    "datePublished": "2025-08-08T16:42:50.517770+03:00",
                                    "dateModified": "2025-08-08T16:42:50.517770+03:00",
                                },
                            ],
                        },
                        {
                            "id": "828f56f4d3b54e3c8d3e262c80052e46",
                            "status": "pending",
                            "documents": [
                                {
                                    "confidentiality": "public",
                                    "hash": "md5:53a994d967c6bac2c6fb613190eacffc",
                                    "title": "sign.p7s",
                                    "documentType": "notice",
                                    "format": "application/pkcs7-signature",
                                    "url": "/tenders/15c1322a6b3e431d9129e6dbf06c9249/cancellations/828f56f4d3b54e3c8d3e262c80052e45/documents/2c2665b1ac404065bfe8dfed7900ec9a?download=0ddec4f9dde247718ad3e841def675e2",
                                    "documentOf": "tender",
                                    "language": "uk",
                                    "id": "2c2665b1ac404065bfe8dfed7900ec9a",
                                    "datePublished": "2025-08-08T16:42:50.517770+03:00",
                                    "dateModified": "2025-08-08T16:42:50.517770+03:00",
                                },
                                {
                                    "confidentiality": "public",
                                    "hash": "md5:53a994d967c6bac2c6fb613190eacffc",
                                    "title": "sign.p7s",
                                    "documentType": "notice",
                                    "format": "application/pkcs7-signature",
                                    "url": "/tenders/15c1322a6b3e431d9129e6dbf06c9249/cancellations/828f56f4d3b54e3c8d3e262c80052e45/documents/2c2665b1ac404065bfe8dfed7900ec9a?download=0ddec4f9dde247718ad3e841def675e2",
                                    "documentOf": "tender",
                                    "language": "uk",
                                    "id": "2c2665b1ac404065bfe8dfed7900ec9b",
                                    "datePublished": "2025-08-08T16:42:50.517770+03:00",
                                    "dateModified": "2025-08-08T16:42:50.517770+03:00",
                                },
                            ],
                        },
                    ],
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
                        "_id": "39e5353444754b2fbe42bf0282ac9513",
                        "_rev": "1-b2e0f794769c490bacdb8053df816d13",
                    },
                    [
                        {
                            "$set": {
                                "_id": "39e5353444754b2fbe42bf0282ac9513",
                                "_rev": "1-b2e0f794769c490bacdb8053df816d13",
                                "cancellations": [
                                    {
                                        "id": "828f56f4d3b54e3c8d3e262c80052e45",
                                        "status": "pending",
                                        "documents": [
                                            {
                                                "confidentiality": "public",
                                                "hash": "md5:5e1fc8654c080f2e89cc5bd2b1aa1d26",
                                                "title": "IMG_20231118_214039 (copy).jpg",
                                                "format": "image/jpeg",
                                                "url": "/tenders/15c1322a6b3e431d9129e6dbf06c9249/cancellations/828f56f4d3b54e3c8d3e262c80052e45/documents/a1bd66bef1e44248a3030d0d2b9affe1?download=893133c08cd545abb6c8dfd457d685f2",
                                                "documentOf": "tender",
                                                "language": "uk",
                                                "id": "a1bd66bef1e44248a3030d0d2b9affe1",
                                                "datePublished": "2025-08-08T16:42:21.597759+03:00",
                                                "dateModified": "2025-08-08T16:42:21.597759+03:00",
                                            },
                                            {
                                                "confidentiality": "public",
                                                "hash": "md5:53a994d967c6bac2c6fb613190eacffc",
                                                "title": "sign.p7s",
                                                "format": "application/pkcs7-signature",
                                                "url": "/tenders/15c1322a6b3e431d9129e6dbf06c9249/cancellations/828f56f4d3b54e3c8d3e262c80052e45/documents/2c2665b1ac404065bfe8dfed7900ec9a?download=0ddec4f9dde247718ad3e841def675e2",
                                                "documentOf": "tender",
                                                "language": "uk",
                                                "id": "2c2665b1ac404065bfe8dfed7900ec9a",
                                                "datePublished": "2025-08-08T16:42:50.517770+03:00",
                                                "dateModified": "2025-08-08T16:42:50.517770+03:00",
                                                "documentType": "cancellationReport",
                                            },
                                        ],
                                    },
                                    {
                                        "id": "828f56f4d3b54e3c8d3e262c80052e46",
                                        "status": "pending",
                                        "documents": [
                                            {
                                                "confidentiality": "public",
                                                "hash": "md5:53a994d967c6bac2c6fb613190eacffc",
                                                "title": "sign.p7s",
                                                "format": "application/pkcs7-signature",
                                                "url": "/tenders/15c1322a6b3e431d9129e6dbf06c9249/cancellations/828f56f4d3b54e3c8d3e262c80052e45/documents/2c2665b1ac404065bfe8dfed7900ec9a?download=0ddec4f9dde247718ad3e841def675e2",
                                                "documentOf": "tender",
                                                "language": "uk",
                                                "id": "2c2665b1ac404065bfe8dfed7900ec9a",
                                                "datePublished": "2025-08-08T16:42:50.517770+03:00",
                                                "dateModified": "2025-08-08T16:42:50.517770+03:00",
                                                "documentType": "cancellationReport",
                                            },
                                            {
                                                "confidentiality": "public",
                                                "hash": "md5:53a994d967c6bac2c6fb613190eacffc",
                                                "title": "sign.p7s",
                                                "format": "application/pkcs7-signature",
                                                "url": "/tenders/15c1322a6b3e431d9129e6dbf06c9249/cancellations/828f56f4d3b54e3c8d3e262c80052e45/documents/2c2665b1ac404065bfe8dfed7900ec9a?download=0ddec4f9dde247718ad3e841def675e2",
                                                "documentOf": "tender",
                                                "language": "uk",
                                                "id": "2c2665b1ac404065bfe8dfed7900ec9b",
                                                "datePublished": "2025-08-08T16:42:50.517770+03:00",
                                                "dateModified": "2025-08-08T16:42:50.517770+03:00",
                                                "documentType": "cancellationReport",
                                            },
                                        ],
                                    },
                                ],
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
                                            {"op": "remove", "path": "/cancellations/0/documents/1/documentType"},
                                            {
                                                "op": "replace",
                                                "path": "/cancellations/1/documents/0/documentType",
                                                "value": "notice",
                                            },
                                            {
                                                "op": "replace",
                                                "path": "/cancellations/1/documents/1/documentType",
                                                "value": "notice",
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
                        {
                            "$set": {
                                "dateModified": ANY,
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
