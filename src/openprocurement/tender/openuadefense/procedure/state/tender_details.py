from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixin
from openprocurement.tender.openuadefense.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS,
    WORKING_DAYS_CONFIG,
)


class DefenseTenderDetailsState(TenderDetailsMixin, TenderState):
    award_class = Award

    items_zero_quantity_check = False
    procuring_entity_available_language_default = "uk"
    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = True
    notice_doc_required_check = False
    vat_not_included_check = False
    working_days_config = WORKING_DAYS_CONFIG
    calendar = WORKING_DAYS
    tender_patch_allowed_statuses = ("draft", "active.tendering", "active.pre-qualification")
    guarantee_criterion_check = False
    related_lot_in_items_check = False
