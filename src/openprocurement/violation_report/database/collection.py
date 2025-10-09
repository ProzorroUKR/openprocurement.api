import logging

from pymongo import ASCENDING, IndexModel

from openprocurement.api.database_async import BaseCollection

logger = logging.getLogger(__name__)


class ViolationReportCollection(BaseCollection):
    object_name = "violation_reports"
    collection_name = "open_violation_reports"

    def get_indexes(self) -> list[IndexModel]:
        # Making multiple indexes with the same unique key is supposed to be impossible
        # https://jira.mongodb.org/browse/SERVER-25023
        # and https://docs.mongodb.com/manual/core/index-partial/#restrictions
        # ``In MongoDB, you cannot create multiple versions of an index that differ only in the options.
        #   As such, you cannot create multiple partial indexes that differ only by the filter expression.``
        # Hold my 🍺
        test_by_public_modified = IndexModel(
            [("public_modified", ASCENDING), ("existing_key", ASCENDING)],
            name="test_by_public_modified",
            partialFilterExpression={
                "is_test": True,
                "is_public": True,
            },
        )
        real_by_public_modified = IndexModel(
            [("public_modified", ASCENDING)],
            name="real_by_public_modified",
            partialFilterExpression={
                "is_test": False,
                "is_public": True,
            },
        )
        all_by_public_modified = IndexModel(
            [
                ("public_modified", ASCENDING),
                ("surely_existing_key", ASCENDING),
            ],  # makes key unique https://jira.mongodb.org/browse/SERVER-25023
            name="all_by_public_modified",
            partialFilterExpression={
                "is_public": True,
            },
        )

        # add unique constraint to prevent duplicates
        unique_violation_report_constrain = IndexModel(
            [
                ("tender_id", ASCENDING),
                ("buyer.identifier.id", ASCENDING),
                ("suppliers.identifier.id", ASCENDING),
            ],
            unique=True,
            name="unique_violation_report_constrain",
        )

        return [
            test_by_public_modified,
            real_by_public_modified,
            all_by_public_modified,
            unique_violation_report_constrain,
        ]
