from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState
from openprocurement.tender.esco.procedure.models.award import Award
from openprocurement.tender.esco.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.awarding import add_next_award


class ESCOTenderTenderState(OpenEUTenderState):
    contract_model = Contract

    @staticmethod
    def add_next_award(request):
        add_next_award(request, award_class=Award)
