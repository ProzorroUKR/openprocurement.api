from logging import getLogger

from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.planning.api.procedure.serializers.plan import PlanRevisionsSerializer
from openprocurement.planning.api.procedure.views.base import PlanBaseResource

LOGGER = getLogger(__name__)


@resource(
    name="Plan Revisions",
    path="/plans/{plan_id}/revisions",
    description="Plan revisions",
)
class PlansRevisionsResource(PlanBaseResource):
    serializer_class = PlanRevisionsSerializer

    @json_view(permission="revision_plan")
    def get(self):
        plan = self.request.validated["plan"]
        return {"data": self.serializer_class(plan).data}
