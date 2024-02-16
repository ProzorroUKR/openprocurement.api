from cornice.resource import resource
from pyramid.security import Allow

from openprocurement.api.utils import json_view
from openprocurement.api.views.base import BaseResource


@resource(
    name="Complaint search",
    path="/complaints/search",
    description="Complaint search",
)
class ComplaintsResource(BaseResource):
    def __acl__(self):
        acl = [
            (Allow, "g:bots", "search_complaints"),
        ]
        return acl

    @json_view(
        permission="search_complaints",
    )
    def get(self):
        complaint_id = self.request.params.get("complaint_id", "")
        results = self.request.registry.mongodb.tenders.find_complaints(complaint_id=complaint_id)
        return {"data": results}
