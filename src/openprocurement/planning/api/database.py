from openprocurement.api.database import BaseCollection
from openprocurement.api.context import get_db_session


class PlanCollection(BaseCollection):
    object_name = "plan"

    def get_field_history(self, uid, *fields):
        projection = {k: True for k in fields}
        projection["revisions"] = True
        res = self.collection.find_one(
            {'_id': uid},
            projection=projection,
            session=get_db_session(),
        )
        return res
