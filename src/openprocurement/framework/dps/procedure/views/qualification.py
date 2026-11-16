from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.qualification import (
    QualificationsResource,
)
from openprocurement.framework.dps.procedure.state.framework import DPSFrameworkState


@resource(
    name=f"{FrameworkType.DYNAMIC_PURCHASING_SYSTEM}:Qualifications",
    collection_path="/qualifications",
    path="/qualifications/{qualification_id}",
    description=f"{FrameworkType.DYNAMIC_PURCHASING_SYSTEM} qualifications",
    qualificationType=FrameworkType.DYNAMIC_PURCHASING_SYSTEM,
    accept="application/json",
)
class DPSQualificationResource(QualificationsResource):
    state_class = DPSFrameworkState

    @json_view(
        content_type="application/json",
        permission="edit_qualification",
    )
    def patch(self):
        return super().patch()
