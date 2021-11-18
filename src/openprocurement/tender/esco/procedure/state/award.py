from openprocurement.tender.esco.procedure.state.tender import ESCOTenderTenderState
from openprocurement.tender.openua.procedure.state.award import AwardState as BaseAwardState


class AwardState(ESCOTenderTenderState, BaseAwardState):
    pass

