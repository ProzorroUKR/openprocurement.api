from openprocurement.api.context import get_request
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import validate_json_data
from openprocurement.framework.core.procedure.models.framework import (
    FrameworkChronographData,
)
from openprocurement.framework.core.procedure.state.framework import (
    FrameworkConfigMixin,
    FrameworkState,
)
from openprocurement.framework.dps.procedure.models.framework import (
    PatchActiveFramework,
    PatchFramework,
)
from openprocurement.framework.dps.procedure.state.qualification import (
    DPSQualificationState,
)
from openprocurement.framework.dps.procedure.state.submission import DPSSubmissionState


class DPSFrameworkConfigMixin(FrameworkConfigMixin):
    def on_post(self, data):
        super().on_post(data)
        self.validate_restricted_derivatives_config(data)

    def on_patch(self, before, after):
        self.validate_restricted_derivatives_config(after)
        super().on_patch(before, after)

    def validate_restricted_derivatives_config(self, data):
        config = data["config"]
        is_defense = data.get("procuringEntity", {}).get("kind") == "defense"
        restricted_derivatives = config.get("restrictedDerivatives")

        if is_defense and restricted_derivatives is False:
            raise_operation_error(
                self.request,
                ["restrictedDerivatives must be true for defense procuring entity"],
                status=422,
                name="restrictedDerivatives",
            )
        elif not is_defense and restricted_derivatives is True:
            raise_operation_error(
                self.request,
                ["restrictedDerivatives must be false for non-defense procuring entity"],
                status=422,
                name="restrictedDerivatives",
            )


class DPSFrameworkState(DPSFrameworkConfigMixin, FrameworkState):
    qualification_class = DPSQualificationState
    submission_class = DPSSubmissionState
    working_days = True

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
