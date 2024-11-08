from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class AwardState(AwardStateMixing, RequestForProposalTenderState):
    pass
