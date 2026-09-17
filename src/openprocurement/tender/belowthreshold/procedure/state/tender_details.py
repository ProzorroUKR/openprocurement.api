from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.belowthreshold.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)
from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.models.tender import PatchActiveTender, PatchDraftTender
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)


class BelowThresholdTenderDetailsMixing(TenderDetailsMixing):
    should_validate_status_change_with_lot_cancellation_pending = False
    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = True
    should_validate_notice_doc_required = True
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.enquiries")

    working_days_config = WORKING_DAYS_CONFIG
    enquiry_period_required = True
    patch_status_choices = (
        "draft",
        "active.enquiries",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
    tender_patch_models_by_status = {
        "active.tendering": PatchActiveTender,
        "draft": PatchDraftTender,
        "active.enquiries": PatchDraftTender,
    }


class BelowThresholdTenderDetailsState(BelowThresholdTenderDetailsMixing, BelowThresholdTenderState):
    pass
