from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.requestforproposal.procedure.state.tender_details import (
    RequestForProposalTenderDetailsState,
)


class TenderLotState(LotStateMixin, RequestForProposalTenderDetailsState):
    lot_operation_allowed_tender_statuses = ("active.enquiries", "active.tendering", "draft")
    pass
