from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.qualification import (
    QualificationsResource,
)
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.dps.procedure.state.framework import DPSFrameworkState


@resource(
    name=f"{DPS_TYPE}:Qualifications",
    collection_path="/qualifications",
    path="/qualifications/{qualification_id}",
    description=f"{DPS_TYPE} qualifications",
    qualificationType=DPS_TYPE,
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
