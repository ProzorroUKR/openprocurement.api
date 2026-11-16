from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.framework import FrameworksResource
from openprocurement.framework.ifi.procedure.state.framework import IFIFrameworkState


@resource(
    name=f"{FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS}:Frameworks",
    collection_path="/frameworks",
    path="/frameworks/{framework_id}",
    description=f"{FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS} frameworks",
    frameworkType=FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS,
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
