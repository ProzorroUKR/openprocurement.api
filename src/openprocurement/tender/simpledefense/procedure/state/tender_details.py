from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.tender.openuadefense.procedure.state.tender_details import (
    DefenseTenderDetailsState,
)
from openprocurement.tender.simpledefense.constants import TENDERING_EXTRA_PERIOD


class SimpleDefenseTenderDetailsState(DefenseTenderDetailsState):
    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_complain_regulation_working_days = True
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.tendering")
