from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.qualification import (
    QualificationsResource,
)
from openprocurement.framework.ifi.constants import IFI_TYPE
from openprocurement.framework.ifi.procedure.state.framework import IFIFrameworkState


@resource(
    name=f"{IFI_TYPE}:Qualifications",
    collection_path="/qualifications",
    path="/qualifications/{qualification_id}",
    description=f"{IFI_TYPE} qualifications",
    qualificationType=IFI_TYPE,
    accept="application/json",
)
class IFIQualificationResource(QualificationsResource):
    state_class = IFIFrameworkState

    @json_view(
        content_type="application/json",
        permission="edit_qualification",
    )
    def patch(self):
        return super().patch()
