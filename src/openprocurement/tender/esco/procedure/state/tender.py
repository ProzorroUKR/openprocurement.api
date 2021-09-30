from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState
from openprocurement.tender.esco.procedure.models.award import Award
from openprocurement.tender.esco.procedure.models.contract import Contract


class ESCOTenderTenderState(OpenEUTenderState):
    contract_model = Contract
    award_class = Award
