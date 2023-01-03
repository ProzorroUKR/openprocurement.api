from openprocurement.tender.openuadefense.procedure.state.tender_details import DefenseTenderDetailsState
from openprocurement.tender.simpledefense.constants import (
    TENDERING_EXTRA_PERIOD,
    ENQUIRY_PERIOD_TIME,
    ENQUIRY_STAND_STILL_TIME,
)


class SimpleDefenseTenderDetailsState(DefenseTenderDetailsState):
    tendering_period_extra = TENDERING_EXTRA_PERIOD

    enquiry_period_timedelta = - ENQUIRY_PERIOD_TIME
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME
