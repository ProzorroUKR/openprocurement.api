from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixing


class CancellationState(CancellationStateMixing, TenderState):
    cancellation_unsuccessful_items_check = True
