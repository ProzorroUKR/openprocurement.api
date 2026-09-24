from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.openuadefense.constants import WORKING_DAYS
from openprocurement.tender.simpledefense.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)


class SimpleDefenseTenderDetailsState(TenderDetailsMixing, TenderState):
    award_class = Award

    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    should_validate_items_zero_quantity = False
    procuring_entity_available_language_default = "uk"
    tender_period_extra_working_days = True
    should_validate_notice_doc_required = False
    should_validate_vat_not_included = False
    calendar = WORKING_DAYS
    items_classification_prefix_change_check = True
    patch_status_choices = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
    items_delivery_required = True
    tender_period_start_date_required = True
    tender_patch_allowed_statuses = (
        "draft",
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
    tender_period_extra = TENDERING_EXTRA_PERIOD
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.tendering")
    working_days_config = WORKING_DAYS_CONFIG
