from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsState,
)
from openprocurement.tender.openuadefense.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS,
    WORKING_DAYS_CONFIG,
)


class DefenseTenderDetailsState(OpenUATenderDetailsState):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    tender_period_extra = TENDERING_EXTRA_PERIOD
    tender_period_extra_working_days = True
    should_validate_notice_doc_required = False
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft", "active.tendering")

    working_days_config = WORKING_DAYS_CONFIG

    calendar = WORKING_DAYS


class AboveThresholdUADefenseTenderDetailsState(DefenseTenderDetailsState):
    should_validate_related_lot_in_items = False
