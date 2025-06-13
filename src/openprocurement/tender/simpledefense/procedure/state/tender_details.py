from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.openuadefense.procedure.state.tender_details import (
    DefenseTenderDetailsState,
)
from openprocurement.tender.simpledefense.constants import (
    ENQUIRY_PERIOD_TIME,
    TENDERING_EXTRA_PERIOD,
)


class SimpleDefenseTenderDetailsState(DefenseTenderDetailsState):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    tendering_period_extra = TENDERING_EXTRA_PERIOD
    enquiry_period_timedelta = -ENQUIRY_PERIOD_TIME
    tender_complain_regulation_working_days = True
    contract_template_required = True
    contract_template_name_patch_statuses = ("draft", "active.tendering")
