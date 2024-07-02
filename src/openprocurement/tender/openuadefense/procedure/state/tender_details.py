from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsState,
)
from openprocurement.tender.openuadefense.constants import (
    COMPLAINT_SUBMIT_TIME,
    ENQUIRY_PERIOD_TIME,
    TENDERING_EXTRA_PERIOD,
)


class DefenseTenderDetailsState(OpenUATenderDetailsState):
    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)

    tendering_period_extra = TENDERING_EXTRA_PERIOD
    complaint_submit_time = COMPLAINT_SUBMIT_TIME
    tendering_period_extra_working_days = True

    enquiry_period_timedelta = -ENQUIRY_PERIOD_TIME
    tender_period_working_day = True

    @classmethod
    def validate_required_criteria(cls, before, after):
        pass


class AboveThresholdUADefenseTenderDetailsState(DefenseTenderDetailsState):
    def validate_related_lot_in_items(self, after):
        pass
