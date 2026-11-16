from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.qualification import (
    QualificationsResource,
)
from openprocurement.framework.ifi.procedure.state.framework import IFIFrameworkState


@resource(
    name=f"{FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS}:Qualifications",
    collection_path="/qualifications",
    path="/qualifications/{qualification_id}",
    description=f"{FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS} qualifications",
    qualificationType=FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS,
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
