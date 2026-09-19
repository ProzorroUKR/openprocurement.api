from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState


class OpenTenderState(TenderState):
    award_class = Award
