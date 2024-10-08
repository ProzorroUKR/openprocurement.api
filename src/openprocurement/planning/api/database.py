from openprocurement.api.context import get_db_session
from openprocurement.api.database import BaseCollection


class PlanCollection(BaseCollection):
    object_name = "plan"

    def save(self, data, insert=False, modified=True):
        self.store.save_data(self.collection, data, insert=insert, modified=modified)

    def get_field_history(self, uid, *fields):
        projection = {k: True for k in fields}
        projection["revisions"] = True
        res = self.collection.find_one(
            {"_id": uid},
            projection=projection,
            session=get_db_session(),
        )
        return res
