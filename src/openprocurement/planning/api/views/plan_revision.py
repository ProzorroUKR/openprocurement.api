from openprocurement.planning.api.utils import opresource
from openprocurement.api.views.base import BaseResource
from openprocurement.api.utils import json_view


@opresource(
    name="Plan Revisions",
    collection_path="/plans/{plan_id}/revisions",
    path="/plans/{plan_id}/revisions/{revision_id}",
    description="Plan revisions",
)
class PlansRevisionResource(BaseResource):
    @json_view(permission="revision_plan")
    def collection_get(self):
        """Plan Revisions List"""
        plan = self.request.validated["plan"]
        plan_revisions = plan.serialize("revision")
        return {"data": plan_revisions}
