from openprocurement.tender.openua.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.openuadefense.constants import (
    TENDERING_EXTRA_PERIOD,
    ENQUIRY_PERIOD_TIME,
    ENQUIRY_STAND_STILL_TIME,
)


class DefenseTenderDetailsState(TenderDetailsState):
    tendering_period_extra = TENDERING_EXTRA_PERIOD
    tendering_period_extra_working_days = True

    enquiry_period_timedelta = - ENQUIRY_PERIOD_TIME
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME
    period_working_day = True

    @staticmethod
    def validate_tender_exclusion_criteria(before, after):
        pass

    @staticmethod
    def validate_tender_language_criteria(before, after):
        pass
