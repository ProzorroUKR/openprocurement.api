from openprocurement.tender.core.procedure.state.review_request import (
    ReviewRequestStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import (
    BelowThresholdTenderState,
    RFPTenderState,
)


class BelowThresholdReviewRequestState(ReviewRequestStateMixin, BelowThresholdTenderState):
    pass


class RFPReviewRequestState(ReviewRequestStateMixin, RFPTenderState):
    pass
