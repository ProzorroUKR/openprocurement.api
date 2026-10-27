from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.framework import FrameworksResource
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.dps.procedure.state.framework import DPSFrameworkState


@resource(
    name=f"{DPS_TYPE}:Frameworks",
    collection_path="/frameworks",
    path="/frameworks/{framework_id}",
    description=f"{DPS_TYPE} frameworks",
    frameworkType=DPS_TYPE,
    accept="application/json",
)
class DPSFrameworkResource(FrameworksResource):
    state_class = DPSFrameworkState

    @json_view(
        content_type="application/json",
        permission="create_framework",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_framework",
    )
    def patch(self):
        return super().patch()
