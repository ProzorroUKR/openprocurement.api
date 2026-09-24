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
    TenderDetailsMixin,
)


class BelowThresholdTenderDetailsMixin(TenderDetailsMixin):
    tender_patch_models_by_status = {
        "active.tendering": PatchActiveTender,
        "draft": PatchDraftTender,
        "active.enquiries": PatchDraftTender,
    }

    tender_create_accreditations = (AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_5)
    tender_edit_accreditations = (AccreditationLevel.ACCR_2,)

    tender_patch_allowed_statuses = (
        "draft",
        "active.enquiries",
        "active.pre-qualification",  # state class only allows status change (pre-qualification.stand-still)
        "active.pre-qualification.stand-still",
    )
    tender_patch_allowed_statuses_for_funder = ("active.tendering",)
    status_change_with_lot_cancellation_pending_check = False
    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = True
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
    vat_not_included_check = False
    items_classification_prefix_change_check = False
    items_delivery_required = False
    tender_period_start_date_required = False


class BelowThresholdTenderDetailsState(BelowThresholdTenderDetailsMixin, BelowThresholdTenderState):
    pass
