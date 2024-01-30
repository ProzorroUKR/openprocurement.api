from openprocurement.tender.core.procedure.state.review_request import ReviewRequestStateMixin
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState


class ReviewRequestState(ReviewRequestStateMixin, BelowThresholdTenderState):
    pass
