from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.models.tender import PatchActiveTender, PatchDraftTender
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixin,
)
from openprocurement.tender.requestforproposal.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RFPTenderState,
)


class RFPTenderDetailsMixin(TenderDetailsMixin):
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
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.tendering",
    )
    status_change_with_lot_cancellation_pending_check = False
    tender_period_extra = TENDERING_EXTRA_PERIOD
    notice_doc_required_check = False
    evaluation_reports_doc_required_check = False
    items_classifications_prefix_check = False
    contract_template_name_patch_statuses = ("draft", "active.enquiries", "active.tendering")
    working_days_config = WORKING_DAYS_CONFIG
    enquiry_period_required = True
    patch_status_choices = (
        "draft",
        "active.enquiries",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
    notice_publication_date_on_activation = True
    vat_not_included_check = False
    items_classification_prefix_change_check = False
    items_delivery_required = False
    tender_period_start_date_required = False


class RFPTenderDetailsState(RFPTenderDetailsMixin, RFPTenderState):
    pass
