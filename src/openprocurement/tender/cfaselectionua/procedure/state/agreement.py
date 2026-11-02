from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.cfaselectionua.procedure.models.agreement import (
    CFASelectionAgreement,
    CFASelectionPatchAgreement,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.utils import dt_from_iso


class CFASelectionAgreementStateMixin:
    patch_data_model = CFASelectionPatchAgreement
    data_model = CFASelectionAgreement

    def validate_agreement_patch_request(self):
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "agreement")
        if self.request.validated["data"]:
            self.validate_agreement_changes_date_signed(self.request.validated["data"])

    def validate_agreement_changes_date_signed(self, agreement):
        errors = [
            {"dateSigned": ["Agreement signature date can't be in the future"]}
            for change in agreement.get("changes") or ""
            if change.get("dateSigned") and dt_from_iso(change["dateSigned"]) > get_request_now()
        ]
        if errors:
            raise_operation_error(self.request, errors, status=422, name="changes")

    def validate_agreement_on_patch(self, *_):
        pass

    def agreement_on_patch(self, before, award):
        request = get_request()
        tender = get_tender()
        tender_status = tender["status"]
        if tender_status != "draft.pending":
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} agreement in current ({tender_status}) tender status",
            )


# example use
class CFASelectionAgreementState(CFASelectionAgreementStateMixin, CFASelectionTenderState):
    pass
