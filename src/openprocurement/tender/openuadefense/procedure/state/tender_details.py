from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsState,
)
from openprocurement.tender.openuadefense.constants import (
    ENQUIRY_PERIOD_TIME,
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS,
)


class DefenseTenderDetailsState(OpenUATenderDetailsState):
    tender_create_accreditations = (AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5)
    tender_central_accreditations = (AccreditationLevel.ACCR_5,)
    tender_edit_accreditations = (AccreditationLevel.ACCR_4,)

    tendering_period_extra = TENDERING_EXTRA_PERIOD
    tendering_period_extra_working_days = True
    enquiry_period_timedelta = -ENQUIRY_PERIOD_TIME
    tender_period_working_day = True
    period_working_day = True
    tender_complain_regulation_working_days = True
    should_validate_notice_doc_required = False
    contract_template_required = False
    contract_template_name_patch_statuses = ("draft", "active.tendering")

    calendar = WORKING_DAYS

    def validate_required_criteria(self, before, after):
        pass


class AboveThresholdUADefenseTenderDetailsState(DefenseTenderDetailsState):
    should_validate_related_lot_in_items = False
