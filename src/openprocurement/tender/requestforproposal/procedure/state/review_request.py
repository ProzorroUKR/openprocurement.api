from openprocurement.tender.core.procedure.state.review_request import (
    ReviewRequestStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class ReviewRequestState(ReviewRequestStateMixin, RequestForProposalTenderState):
    pass
