from openprocurement.api.context import get_request
from openprocurement.framework.core.procedure.models.framework import FrameworkChronographData
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.electroniccatalogue.procedure.models.framework import (
    PatchActiveFramework,
    PatchFramework,
)
from .qualification import ElectronicDialogueQualificationState
from .submission import ElectronicDialogueSubmissionState


class ElectronicDialogueFrameworkState(FrameworkState):
    qualification_class = ElectronicDialogueQualificationState
    submission_class = ElectronicDialogueSubmissionState

    def get_patch_data_model(self):
        request = get_request()
        validated_framework = request.validated["framework"]
        status = validated_framework["status"]
        request_data = request.json["data"]
        new_status = request_data.get("status") or status

        if request.authenticated_role == "chronograph":
            return FrameworkChronographData
        elif new_status == "active":
            return PatchActiveFramework
        return PatchFramework
