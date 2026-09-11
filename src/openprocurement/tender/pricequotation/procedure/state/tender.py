from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState


class PriceQuotationTenderState(TenderState):
    award_class = Award
    generate_award_milestones = False
    award_period_duration = 2
