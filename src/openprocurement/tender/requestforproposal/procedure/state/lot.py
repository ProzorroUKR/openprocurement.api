from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.requestforproposal.procedure.state.tender_details import (
    RequestForProposalTenderDetailsState,
)


class TenderLotState(LotStateMixin, RequestForProposalTenderDetailsState):
    pass
