from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.framework import FrameworksResource
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.framework.electroniccatalogue.procedure.state.framework import (
    ElectronicDialogueFrameworkState,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Frameworks",
    collection_path="/frameworks",
    path="/frameworks/{framework_id}",
    description=f"{ELECTRONIC_CATALOGUE_TYPE} frameworks",
    frameworkType=ELECTRONIC_CATALOGUE_TYPE,
    accept="application/json",
)
class ElectronicCatalogueFrameworkResource(FrameworksResource):
    state_class = ElectronicDialogueFrameworkState

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
