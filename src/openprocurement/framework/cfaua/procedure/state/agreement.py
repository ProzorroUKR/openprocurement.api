from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.context import get_request
from openprocurement.api.procedure.state.base import BaseState, ConfigMixin
from openprocurement.api.procedure.validation import validate_patch_input_data_from_resolved_model
from openprocurement.api.utils import raise_operation_error
from openprocurement.framework.cfaua.procedure.models.agreement import (
    Agreement,
    PatchActiveAgreement,
    PatchAgreementByAdministrator,
    PatchTerminatedAgreement,
    PostAgreement,
)
from openprocurement.framework.cfaua.procedure.validation import validate_related_item
from openprocurement.framework.core.procedure.utils import is_tender_owner


class AgreementConfigMixin(ConfigMixin):
    default_config_schema = {
        "type": "object",
        "properties": {
            "restricted": {"type": "boolean"},
            "test": {"type": "boolean"},
        },
    }


class AgreementState(BaseState, AgreementConfigMixin):
    post_data_model = PostAgreement
    data_model = Agreement

    agreement_create_accreditations: tuple = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)

    # --- request validation (called from the views) ---

    def validate_agreement_post_request(self):
        self.validate_input_data(self.get_post_data_model())
        self.validate_config_data()
        self.validate_accreditation_level(
            levels=self.agreement_create_accreditations,
            item="agreement",
            operation="creation",
            source="data",
        )

    def validate_agreement_patch_request(self):
        if self.request.authenticated_role != "Administrator":
            self.validate_item_owner("agreement")
        validate_patch_input_data_from_resolved_model()(self.request)
        self.validate_patch_data(self.get_data_model(), item_name="agreement")
        self.validate_agreement_termination()

    def validate_credentials_patch_request(self):
        if not is_tender_owner(self.request, self.request.validated["agreement"]):
            raise_operation_error(self.request, "Forbidden", location="url", name="permission")
        status = self.request.validated["agreement"]["status"]
        if status != "active":
            raise_operation_error(self.request, f"Can't generate credentials in current ({status}) agreement status")

    def validate_agreement_termination(self):
        """an agreement with a pending change can't be terminated"""
        changes = self.request.validated["agreement"].get("changes")
        if not changes:
            return
        if self.request.validated["data"].get("status") == "terminated" and any(
            change["status"] == "pending" for change in changes
        ):
            raise_operation_error(self.request, "Can't update agreement status with pending change.")

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
