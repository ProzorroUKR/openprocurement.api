from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.qualification import (
    QualificationsResource,
)
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.framework.electroniccatalogue.procedure.state.framework import (
    ElectronicDialogueFrameworkState,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Qualifications",
    collection_path="/qualifications",
    path="/qualifications/{qualification_id}",
    description=f"{ELECTRONIC_CATALOGUE_TYPE} qualifications",
    qualificationType=ELECTRONIC_CATALOGUE_TYPE,
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
