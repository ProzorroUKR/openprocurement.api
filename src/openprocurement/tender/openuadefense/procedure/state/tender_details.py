from openprocurement.tender.openua.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.openuadefense.constants import TENDERING_EXTRA_PERIOD


class DefenseTenderDetailsState(TenderDetailsState):
    tendering_period_extra = TENDERING_EXTRA_PERIOD
    tendering_period_extra_working_days = True


