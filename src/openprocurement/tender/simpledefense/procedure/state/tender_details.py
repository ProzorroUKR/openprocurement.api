from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.openuadefense.procedure.state.tender_details import (
    DefenseTenderDetailsState,
)
from openprocurement.tender.simpledefense.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)


class SimpleDefenseTenderDetailsState(DefenseTenderDetailsState):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.tendering")

    working_days_config = WORKING_DAYS_CONFIG
