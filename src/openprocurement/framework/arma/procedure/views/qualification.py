from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.arma.procedure.state.framework import ARMAFrameworkState
from openprocurement.framework.core.procedure.views.qualification import (
    QualificationsResource,
)


@resource(
    name=f"{ARMA_TYPE}:Qualifications",
    collection_path="/qualifications",
    path="/qualifications/{qualification_id}",
    description=f"{ARMA_TYPE} qualifications",
    qualificationType=ARMA_TYPE,
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
