from openprocurement.api.context import get_request
from openprocurement.framework.cfaua.procedure.models.agreement import (
    PatchActiveAgreement,
    PatchTerminatedAgreement,
    PatchAgreementByAdministrator,
)
from openprocurement.api.procedure.state.base import BaseState


class AgreementState(BaseState):
    def get_patch_data_model(self):
        request = get_request()
        validated_agreement = request.validated["agreement"]
        status = validated_agreement["status"]

        if request.authenticated_role == "Administrator":
            return PatchAgreementByAdministrator
        elif status == "active":
            return PatchActiveAgreement
        return PatchTerminatedAgreement
