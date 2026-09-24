from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.review_request import (
    ReviewRequestStateMixin,
)


class BelowThresholdReviewRequestState(ReviewRequestStateMixin, BelowThresholdTenderState):
    pass
