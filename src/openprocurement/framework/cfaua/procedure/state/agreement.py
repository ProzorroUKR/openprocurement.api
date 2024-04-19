from openprocurement.api.context import get_request
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.framework.cfaua.procedure.models.agreement import (
    PatchActiveAgreement,
    PatchAgreementByAdministrator,
    PatchTerminatedAgreement,
)
from openprocurement.framework.cfaua.procedure.validation import validate_related_item


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

    def on_post(self, data):
        for doc in data.get("documents", []):
            validate_related_item(doc.get("relatedItem"), doc["documentOf"])
        super().on_post(data)

    def on_patch(self, before, after):
        for doc in after.get("documents", []):
            validate_related_item(doc.get("relatedItem"), doc["documentOf"])
        super().on_patch(before, after)
