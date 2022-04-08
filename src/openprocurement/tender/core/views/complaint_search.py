from openprocurement.api.utils import APIResource, opresource, json_view


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
        results = self.request.registry.mongodb.tenders.find_complaints(complaint_id=complaint_id)
        return {"data": results}
