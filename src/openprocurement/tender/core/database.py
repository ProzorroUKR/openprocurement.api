from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.database import BaseCollection
from pymongo import IndexModel, ASCENDING
import logging


logger = logging.getLogger(__name__)


class TenderCollection(BaseCollection):
    object_name = "tender"

    def get_indexes(self):
        indexes = super().get_indexes()

        tender_complaints = IndexModel(
            [("complaints.complaintID", ASCENDING)],
            name="tender_complaints",
            partialFilterExpression={
                "dateCreated": {"$gt": RELEASE_2020_04_19.isoformat()},
            },
        )
        indexes.append(tender_complaints)

        for sub_type in ('qualifications', 'awards', 'cancellations'):
            indexes.append(
                IndexModel(
                    [(f"{sub_type}.complaints.complaintID", ASCENDING)],
                    name=f"{sub_type}_complaints",
                    partialFilterExpression={
                        "dateCreated": {"$gt": RELEASE_2020_04_19.isoformat()},
                    },
                )
            )
        return indexes

    def save(self, data, insert=False, modified=True):
        self.store.save_data(self.collection, data, insert=insert, modified=modified)

    def find_complaints(self, complaint_id: str):
        collection = self.collection
        query = {
            "complaints": {
                "$elemMatch": {"complaintID": complaint_id}
            },
            "dateCreated": {"$gt": RELEASE_2020_04_19.isoformat()},
        }
        result = collection.find_one(query)
        if result:
            return self._prepare_complaint_response(result, complaint_id)

        for sub_type in ('qualifications', 'awards', 'cancellations'):
            query = {
                "dateCreated": {"$gt": RELEASE_2020_04_19.isoformat()},
                sub_type: {"$elemMatch": {"complaints": {"$elemMatch": {"complaintID": complaint_id}}}},
            }
            result = collection.find_one(query)
            if result:
                return self._prepare_complaint_response(result, complaint_id, item_type=sub_type)
        return []

    @staticmethod
    def _prepare_complaint_response(tender, complaint_id, item_type=None):
        response = [
            {
                "params": {
                    "tender_id": tender["_id"],
                    "item_type": item_type,
                    "item_id": i.get("id"),
                    "complaint_id": c["id"],
                },
                "access": {
                    "token": c["owner_token"]
                }
            }
            for i in (tender[item_type] if item_type else [tender])
            for c in i.get("complaints", "")
            if c["complaintID"] == complaint_id
            # pymongo.errors.OperationFailure: Cannot use $elemMatch projection on a nested field
        ]
        return response
