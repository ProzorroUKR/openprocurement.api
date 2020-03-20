from functools import partial

from openprocurement.api.utils import APIResource, opresource, json_view
from openprocurement.tender.core.design import complaints_by_complaint_id_view


@opresource(
    name="Complaint search",
    path="/complaints/search",
    description="Complaint search",
)
class ComplaintsResource(APIResource):
    @json_view(
        permission="search_complaints",
    )
    def get(self):
        complaint_id = self.request.params.get("complaint_id", "").lower()
        if complaint_id:
            view = partial(complaints_by_complaint_id_view, self.db, key=complaint_id)
            results = [x.value for x in view()]
        else:
            results = []
        return {"data": results}
