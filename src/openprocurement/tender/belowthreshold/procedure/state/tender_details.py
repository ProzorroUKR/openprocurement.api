from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.context import get_request_now
from openprocurement.tender.belowthreshold.constants import TENDERING_EXTRA_PERIOD
from openprocurement.tender.belowthreshold.procedure.models.tender import (
    PatchDraftTender,
    PatchTender,
)
from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.belowthreshold.procedure.validation import tender_for_funder
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.requestforproposal.procedure.models.tender import (
    PatchActiveTender,
)


class BelowThresholdTenderDetailsMixing(TenderDetailsMixing):
    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    tendering_period_extra_working_days = True
    tendering_period_extra = TENDERING_EXTRA_PERIOD
    should_validate_notice_doc_required = True
    enquiry_before_tendering = True
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.enquiries")

    def get_patch_data_model(self):
        tender = self.request.validated["tender"]
        if tender.get("status", "") == "active.tendering":
            return PatchActiveTender
        elif tender.get("status", "") in ("draft", "active.enquiries"):
            return PatchDraftTender
        return PatchTender

    def validate_tender_period_extension(self, tender):
        if tender_for_funder(tender):
            super().validate_tender_period_extension(tender)

    @staticmethod
    def set_enquiry_period_invalidation_date(tender):
        if tender_for_funder(tender):
            tender["enquiryPeriod"]["invalidationDate"] = get_request_now().isoformat()

    def invalidate_bids_data(self, tender):
        if tender_for_funder(tender):
            super().invalidate_bids_data(tender)


class BelowThresholdTenderDetailsState(BelowThresholdTenderDetailsMixing, BelowThresholdTenderState):
    pass
