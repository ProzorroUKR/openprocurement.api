from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.models.qualification import PatchQualification
from openprocurement.framework.core.procedure.validation import (
    validate_framework_owner,
    validate_action_in_not_allowed_framework_status,
    validate_update_qualification_in_not_allowed_status,
)
from openprocurement.framework.core.procedure.views.qualification import QualificationsResource
from openprocurement.framework.electroniccatalogue.constants import ELECTRONIC_CATALOGUE_TYPE
from openprocurement.framework.electroniccatalogue.procedure.models.qualification import Qualification
from openprocurement.framework.electroniccatalogue.procedure.state.framework import (
    ElectronicDialogueFrameworkState,
)
from openprocurement.framework.electroniccatalogue.procedure.state.qualification import (
    ElectronicDialogueQualificationState,
)
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    unless_administrator,
    validate_patch_data,
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
        validators=(
                unless_administrator(
                    validate_framework_owner("qualification"),
                ),
                validate_input_data(PatchQualification),
                validate_update_qualification_in_not_allowed_status,
                validate_action_in_not_allowed_framework_status("qualification"),
                validate_patch_data(Qualification, item_name="qualification"),
        ),
        permission="edit_qualification",
    )
    def patch(self):
        return super().patch()
