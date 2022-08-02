from openprocurement.api.database import BaseCollection
from pymongo import ASCENDING, IndexModel


class FrameworkCollection(BaseCollection):
    object_name = "framework"


class SubmissionCollection(BaseCollection):
    object_name = "submission"

    def get_indexes(self):
        indexes = super().get_indexes()
        for_framework_by_public_modified = IndexModel(
            [("frameworkID", ASCENDING),
             ("public_modified", ASCENDING)],
            name="for_framework_by_public_modified",
            partialFilterExpression={
                "is_public": True,
            },
        )
        indexes.append(for_framework_by_public_modified)
        return indexes

    def count_active_submissions_by_framework_id(self, framework_id, identifier_id):
        result = self.collection.count(
            filter={
                "tenderers.identifier.id": identifier_id,
                "status": "active",
                # there is an index for these two below
                "frameworkID": framework_id,
                "is_public": True,
            },
        )
        return result

    def count_total_submissions_by_framework_id(self, framework_id):
        result = self.collection.count(
            filter={
                "status": {"$nin": ["draft", "deleted"]},
                # there is an index for these two below
                "frameworkID": framework_id,
                "is_public": True,
            },
        )
        return result


class AgreementCollection(BaseCollection):
    object_name = "agreement"

    def get_indexes(self):
        indexes = super().get_indexes()
        for_framework_by_public_modified = IndexModel(
            [("frameworkID", ASCENDING),
             ("public_modified", ASCENDING)],
            name="for_framework_by_public_modified",
            partialFilterExpression={
                "is_public": True,
            },
        )
        indexes.append(for_framework_by_public_modified)

        by_classification = IndexModel(
            [("classification.id", ASCENDING)],
            name="by_classification",
            partialFilterExpression={
                "is_public": True,
                "status": "active",
            },
        )
        indexes.append(by_classification)
        return indexes

    def list_by_classification_id(self, classification_id):
        result = list(self.collection.find(
            filter={
                "classification.id": {"$regex": f"^{classification_id}"},
                "is_public": True,
                "status": "active",
            },
            projection=["classification", "additionalClassifications", "status", "id", "contracts", "dateModified"],
        ))
        # print(
        #     self.collection.find(
        #         filter={
        #             "classification.id": {"$regex": f"^{classification_id}"},
        #             "is_public": True,
        #             "status": "active",
        #         },
        #     ).explain()["executionStats"]["executionStages"]
        # )
        return result

    def has_active_suspended_contracts(self, framework_id, identifier_id):
        result = list(self.collection.find(
            filter={
                "contracts": {"$elemMatch": {
                    "status": {"$in": ["active", "suspended"]},
                    "suppliers.identifier.id": identifier_id,
                }},
                # there is an index for these two below
                "frameworkID": framework_id,
                "is_public": True,
            },
            projection=["_id"],
            limit=1,
        ))
        return bool(result)


class QualificationCollection(BaseCollection):
    object_name = "qualification"

