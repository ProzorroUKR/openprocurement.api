from openprocurement.api.auth import ACCR_1, ACCR_2, ACCR_5
from openprocurement.tender.belowthreshold.procedure.models.tender import (
    PatchDraftTender,
    PatchTender,
)
from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)


class BelowThresholdTenderDetailsMixing(TenderDetailsMixing):
    tender_create_accreditations = (ACCR_1, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_2,)

    should_validate_notice_doc_required = True
    enquiry_before_tendering = True
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.enquiries")

    def get_patch_data_model(self):
        tender = self.request.validated["tender"]
        if tender.get("status", "") in ("draft", "active.enquiries"):
            return PatchDraftTender
        return PatchTender

    def validate_tender_period_extension(self, tender):
        pass

    @staticmethod
    def set_enquiry_period_invalidation_date(tender):
        pass

    def invalidate_bids_data(self, tender):
        pass


class BelowThresholdTenderDetailsState(BelowThresholdTenderDetailsMixing, BelowThresholdTenderState):
    pass
