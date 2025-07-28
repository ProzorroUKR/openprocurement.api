import logging
from copy import deepcopy
from unittest.mock import ANY

from pymongo import UpdateOne

from openprocurement.api.migrations.base import CollectionMigration, migrate_collection

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Migration(CollectionMigration):
    description = "Migrate tenders complaint posts"

    collection_name = "tenders"

    append_revision = True

    update_date_modified: bool = False
    update_feed_position: bool = True

    log_every: int = 100000
    bulk_max_size: int = 500

    def get_filter(self):
        return {
            "$or": [
                {"complaints": {"$exists": True}},
                {"awards.complaints": {"$exists": True}},
                {"cancellations.complaints": {"$exists": True}},
                {"qualifications.complaints": {"$exists": True}},
            ]
        }

    def get_projection(self) -> dict:
        return {"complaints": 1, "awards": 1, "cancellations": 1, "qualifications": 1}

    def remove_documents_from_complaint_post(self, obj):
        if "complaints" in obj:
            for complaint in obj["complaints"]:
                if "posts" in complaint:
                    for post in complaint["posts"]:
                        post.pop("documents", None)

    def update_document(self, doc, context=None):
        prev_doc = deepcopy(doc)
        self.remove_documents_from_complaint_post(doc)

        # Process complaints in other tender objects
        for objs in ("awards", "qualifications", "cancellations"):
            if objs in doc:
                for obj in doc[objs]:
                    self.remove_documents_from_complaint_post(obj)

        if prev_doc != doc:
            return doc

        return None

    def run_test(self):
        mock_collection = self.run_test_data(
            [
                {
                    "_id": "39e5353444754b2fbe42bf0282ac951d",
                    "_rev": "1-b2e0f794769c490bacdb8053df816d10",
                    "complaints": [
                        {
                            "posts": [
                                {
                                    "documents": [
                                        {
                                            "confidentiality": "public",
                                            "hash": "md5:00000000000000000000000000000000",
                                            "title": "Complaint_Attachment.pdf",
                                            "format": "application/pdf",
                                            "url": "http://public-docs-sandbox.prozorro.gov.ua/get/58f9d67e04944faa910186f868189357?Signature=bTyysxLgmSxwOJ2mbeKuyIt9n0Kc0GIDrLYtNInWgPLwFyGb0nhul1wcwlTI5Lh7pZFnS9JPCG0ax9wWPt1LAQ%3D%3D&KeyID=a8968c46",
                                            "language": "uk",
                                            "id": "f1772556a53043f78f600eea868406bc",
                                            "documentOf": "tender",
                                            "datePublished": "2023-10-10T01:00:00+03:00",
                                            "dateModified": "2023-10-10T01:00:00+03:00",
                                            "author": "complaint_owner",
                                        }
                                    ],
                                    "id": "f1772556a53043f78f600eea868406bc",
                                }
                            ]
                        }
                    ],
                    "qualifications": [
                        {
                            "id": "4b24f191b1a54048827b46c3a722c239",
                            "bidID": "495527481bb143c7be9a0fcf21dcaee7",
                            "status": "active",
                            "date": "2024-05-17T21:09:41.774693+03:00",
                            "complaints": [
                                {
                                    "posts": [
                                        {
                                            "documents": [
                                                {
                                                    "confidentiality": "public",
                                                    "hash": "md5:00000000000000000000000000000000",
                                                    "title": "Complaint_Attachment.pdf",
                                                    "format": "application/pdf",
                                                    "url": "http://public-docs-sandbox.prozorro.gov.ua/get/58f9d67e04944faa910186f868189357?Signature=bTyysxLgmSxwOJ2mbeKuyIt9n0Kc0GIDrLYtNInWgPLwFyGb0nhul1wcwlTI5Lh7pZFnS9JPCG0ax9wWPt1LAQ%3D%3D&KeyID=a8968c46",
                                                    "language": "uk",
                                                    "id": "f1772556a53043f78f600eea868406bc",
                                                    "documentOf": "tender",
                                                    "datePublished": "2023-10-10T01:00:00+03:00",
                                                    "dateModified": "2023-10-10T01:00:00+03:00",
                                                    "author": "complaint_owner",
                                                }
                                            ],
                                            "id": "f1772556a53043f78f600eea86840600",
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                    "revisions": [
                        {
                            "author": "broker",
                            "changes": [{"op": "remove", "path": "/complaints/0/posts"}],
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
                                "complaints": [{"posts": [{"id": "f1772556a53043f78f600eea868406bc"}]}],
                                "qualifications": [
                                    {
                                        "id": "4b24f191b1a54048827b46c3a722c239",
                                        "bidID": "495527481bb143c7be9a0fcf21dcaee7",
                                        "status": "active",
                                        "date": "2024-05-17T21:09:41.774693+03:00",
                                        "complaints": [
                                            {
                                                "posts": [
                                                    {
                                                        "id": "f1772556a53043f78f600eea86840600",
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                ],
                                "revisions": [
                                    {
                                        "author": "broker",
                                        "changes": [{"op": "remove", "path": "/complaints/0/posts"}],
                                        "rev": None,
                                        "date": "2025-04-23T20:01:57.079339+03:00",
                                    },
                                    {
                                        "author": "migration",
                                        "changes": [
                                            {
                                                "op": "add",
                                                "path": "/complaints/0/posts/0/documents",
                                                "value": [
                                                    {
                                                        "confidentiality": "public",
                                                        "hash": "md5:00000000000000000000000000000000",
                                                        "title": "Complaint_Attachment.pdf",
                                                        "format": "application/pdf",
                                                        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/58f9d67e04944faa910186f868189357?Signature=bTyysxLgmSxwOJ2mbeKuyIt9n0Kc0GIDrLYtNInWgPLwFyGb0nhul1wcwlTI5Lh7pZFnS9JPCG0ax9wWPt1LAQ%3D%3D&KeyID=a8968c46",
                                                        "language": "uk",
                                                        "id": "f1772556a53043f78f600eea868406bc",
                                                        "documentOf": "tender",
                                                        "datePublished": "2023-10-10T01:00:00+03:00",
                                                        "dateModified": "2023-10-10T01:00:00+03:00",
                                                        "author": "complaint_owner",
                                                    }
                                                ],
                                            },
                                            {
                                                "op": "add",
                                                "path": "/qualifications/0/complaints/0/posts/0/documents",
                                                "value": [
                                                    {
                                                        "confidentiality": "public",
                                                        "hash": "md5:00000000000000000000000000000000",
                                                        "title": "Complaint_Attachment.pdf",
                                                        "format": "application/pdf",
                                                        "url": "http://public-docs-sandbox.prozorro.gov.ua/get/58f9d67e04944faa910186f868189357?Signature=bTyysxLgmSxwOJ2mbeKuyIt9n0Kc0GIDrLYtNInWgPLwFyGb0nhul1wcwlTI5Lh7pZFnS9JPCG0ax9wWPt1LAQ%3D%3D&KeyID=a8968c46",
                                                        "language": "uk",
                                                        "id": "f1772556a53043f78f600eea868406bc",
                                                        "documentOf": "tender",
                                                        "datePublished": "2023-10-10T01:00:00+03:00",
                                                        "dateModified": "2023-10-10T01:00:00+03:00",
                                                        "author": "complaint_owner",
                                                    }
                                                ],
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
