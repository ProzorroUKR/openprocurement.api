from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.arma.procedure.state.framework import ARMAFrameworkState
from openprocurement.framework.core.procedure.views.framework import FrameworksResource


@resource(
    name=f"{ARMA_TYPE}:Frameworks",
    collection_path="/frameworks",
    path="/frameworks/{framework_id}",
    description=f"{ARMA_TYPE} frameworks",
    frameworkType=ARMA_TYPE,
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
