from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.awarding import add_next_award as add_award
from openprocurement.tender.openua.procedure.models.award import Award


class OpenUATenderState(TenderState):

    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")

    @staticmethod
    def add_next_award(request):
        add_award(request, award_class=Award)
