from openprocurement.tender.esco.procedure.state.tender import ESCOTenderStateMixin
from openprocurement.tender.openeu.procedure.state.cancellation import OpenEUCancellationState


class ESCOCancellationState(ESCOTenderStateMixin, OpenEUCancellationState):
    pass