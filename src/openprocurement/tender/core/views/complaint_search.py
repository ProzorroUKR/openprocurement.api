from openprocurement.api.utils import opresource, json_view
from openprocurement.api.views.base import BaseResource


@opresource(
    name="Complaint search",
    path="/complaints/search",
    description="Complaint search",
)
class ComplaintsResource(BaseResource):
    @json_view(
        permission="search_complaints",
    )
    def get(self):
        complaint_id = self.request.params.get("complaint_id", "")
        results = self.request.registry.mongodb.tenders.find_complaints(complaint_id=complaint_id)
        return {"data": results}
