from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.belowthreshold.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)
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
from openprocurement.tender.requestforproposal.procedure.models.tender import (
    PatchActiveTender,
)


class BelowThresholdTenderDetailsMixing(TenderDetailsMixing):
    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = True
    should_validate_notice_doc_required = True
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.enquiries")

    working_days_config = WORKING_DAYS_CONFIG

    def get_patch_data_model(self):
        tender = self.request.validated["tender"]
        if tender.get("status", "") == "active.tendering":
            return PatchActiveTender
        elif tender.get("status", "") in ("draft", "active.enquiries"):
            return PatchDraftTender
        return PatchTender


class BelowThresholdTenderDetailsState(BelowThresholdTenderDetailsMixing, BelowThresholdTenderState):
    pass
