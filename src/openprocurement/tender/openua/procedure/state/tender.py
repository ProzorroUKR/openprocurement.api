from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState


class OpenUATenderState(TenderState):
    award_class = Award
