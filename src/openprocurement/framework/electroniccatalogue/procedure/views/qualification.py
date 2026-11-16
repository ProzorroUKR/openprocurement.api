from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.qualification import (
    QualificationsResource,
)
from openprocurement.framework.electroniccatalogue.procedure.state.framework import (
    ElectronicDialogueFrameworkState,
)


@resource(
    name=f"{FrameworkType.ELECTRONIC_CATALOGUE}:Qualifications",
    collection_path="/qualifications",
    path="/qualifications/{qualification_id}",
    description=f"{FrameworkType.ELECTRONIC_CATALOGUE} qualifications",
    qualificationType=FrameworkType.ELECTRONIC_CATALOGUE,
    accept="application/json",
)
class ElectronicCatalogueQualificationResource(QualificationsResource):
    state_class = ElectronicDialogueFrameworkState

    @json_view(
        content_type="application/json",
        permission="edit_qualification",
    )
    def patch(self):
        return super().patch()
