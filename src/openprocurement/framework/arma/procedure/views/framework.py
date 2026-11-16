from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.api.utils import json_view
from openprocurement.framework.arma.procedure.state.framework import ARMAFrameworkState
from openprocurement.framework.core.procedure.views.framework import FrameworksResource


@resource(
    name=f"{FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY}:Frameworks",
    collection_path="/frameworks",
    path="/frameworks/{framework_id}",
    description=f"{FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY} frameworks",
    frameworkType=FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY,
    accept="application/json",
)
class ARMAFrameworkResource(FrameworksResource):
    state_class = ARMAFrameworkState

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
