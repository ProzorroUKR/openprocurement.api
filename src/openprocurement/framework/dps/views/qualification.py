from openprocurement.api.utils import json_view
from openprocurement.framework.core.utils import qualificationsresource
from openprocurement.framework.core.views.qualification import CoreQualificationResource
from openprocurement.framework.core.validation import (
    validate_patch_qualification_data,
    validate_update_qualification_in_not_allowed_status,
    validate_action_in_not_allowed_framework_status,
)
from openprocurement.framework.dps.constants import DPS_TYPE


@qualificationsresource(
    name=f"{DPS_TYPE}:Qualifications",
    path="/qualifications/{qualification_id}",
    qualificationType=DPS_TYPE,
    description="Qualifications",
)
class QualificationResource(CoreQualificationResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_update_qualification_in_not_allowed_status,
            validate_patch_qualification_data,
            validate_action_in_not_allowed_framework_status("qualification"),
        ),
        permission="edit_qualification",
    )
    def patch(self):
        return super().patch()
