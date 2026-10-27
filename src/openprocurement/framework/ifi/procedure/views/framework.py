from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.framework import FrameworksResource
from openprocurement.framework.ifi.constants import IFI_TYPE
from openprocurement.framework.ifi.procedure.state.framework import IFIFrameworkState


@resource(
    name=f"{IFI_TYPE}:Frameworks",
    collection_path="/frameworks",
    path="/frameworks/{framework_id}",
    description=f"{IFI_TYPE} frameworks",
    frameworkType=IFI_TYPE,
    accept="application/json",
)
class IFIFrameworkResource(FrameworksResource):
    state_class = IFIFrameworkState

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
