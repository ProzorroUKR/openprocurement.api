from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.api.utils import json_view
from openprocurement.framework.arma.procedure.state.framework import ARMAFrameworkState
from openprocurement.framework.core.procedure.views.qualification import (
    QualificationsResource,
)


@resource(
    name=f"{FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY}:Qualifications",
    collection_path="/qualifications",
    path="/qualifications/{qualification_id}",
    description=f"{FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY} qualifications",
    qualificationType=FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY,
    accept="application/json",
)
class ARMAQualificationResource(QualificationsResource):
    state_class = ARMAFrameworkState

    @json_view(
        content_type="application/json",
        permission="edit_qualification",
    )
    def patch(self):
        return super().patch()
