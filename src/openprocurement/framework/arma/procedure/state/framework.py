from openprocurement.api.context import get_request
from openprocurement.api.validation import validate_json_data
from openprocurement.framework.arma.procedure.models.framework import (
    PatchActiveFramework,
    PatchFramework,
)
from openprocurement.framework.arma.procedure.state.qualification import (
    ARMAQualificationState,
)
from openprocurement.framework.arma.procedure.state.submission import (
    ARMASubmissionState,
)
from openprocurement.framework.core.procedure.models.framework import (
    FrameworkChronographData,
)
from openprocurement.framework.core.procedure.state.framework import FrameworkState


class ARMAFrameworkState(FrameworkState):
    qualification_class = ARMAQualificationState
    submission_class = ARMASubmissionState
    enquiry_period_lasts_until_qualification = True
    # "unsuccessful framework" mechanism is disabled: submissions are accepted
    # until the framework ends, both values should stay zero
    min_submissions_number = 0
    min_submissions_number_days = 0

    def get_patch_data_model(self):
        request = get_request()
        validated_framework = request.validated["framework"]
        status = validated_framework["status"]
        request_data = validate_json_data(request)
        new_status = request_data.get("status") or status

        if request.authenticated_role == "chronograph":
            return FrameworkChronographData
        elif new_status == "active":
            return PatchActiveFramework
        return PatchFramework
