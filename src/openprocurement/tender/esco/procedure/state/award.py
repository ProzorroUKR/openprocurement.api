from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState
from openprocurement.tender.openua.procedure.state.award import AwardState as BaseAwardState


class AwardState(ESCOTenderState, BaseAwardState):
    pass
