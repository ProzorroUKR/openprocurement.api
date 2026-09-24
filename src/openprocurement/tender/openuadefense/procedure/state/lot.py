from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixin
from openprocurement.tender.openuadefense.constants import LOT_TENDERING_EXTRA_PERIOD


class DefenseTenderLotState(LotStateMixin, TenderDetailsMixin, TenderState):
    award_class = Award

    tender_period_extra = LOT_TENDERING_EXTRA_PERIOD
    contract_template_required = True
