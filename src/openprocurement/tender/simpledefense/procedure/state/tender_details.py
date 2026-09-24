from openprocurement.api.constants import WORKING_DAYS_WITH_WORKING_WEEKENDS
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixin
from openprocurement.tender.simpledefense.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)


class SimpleDefenseTenderDetailsState(TenderDetailsMixin, TenderState):
    award_class = Award

    items_zero_quantity_check = False
    procuring_entity_available_language_default = "uk"
    tender_period_extra_working_days = True
    notice_doc_required_check = False
    vat_not_included_check = False
    calendar = WORKING_DAYS_WITH_WORKING_WEEKENDS
    tender_period_extra = TENDERING_EXTRA_PERIOD
    contract_template_required = True
    working_days_config = WORKING_DAYS_CONFIG
