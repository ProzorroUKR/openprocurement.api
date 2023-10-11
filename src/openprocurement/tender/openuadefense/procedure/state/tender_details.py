from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.tender.openua.procedure.state.tender_details import OpenUATenderDetailsState
from openprocurement.tender.openuadefense.constants import (
    TENDERING_EXTRA_PERIOD,
    ENQUIRY_PERIOD_TIME,
    ENQUIRY_STAND_STILL_TIME,
)


class DefenseTenderDetailsState(OpenUATenderDetailsState):
    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)

    tendering_period_extra = TENDERING_EXTRA_PERIOD
    tendering_period_extra_working_days = True

    enquiry_period_timedelta = - ENQUIRY_PERIOD_TIME
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME
    period_working_day = True

    @classmethod
    def validate_tender_exclusion_criteria(cls, before, after):
        pass

    @staticmethod
    def validate_tender_language_criteria(before, after):
        pass
