from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class NegotiationCancellationComplaintState(CancellationComplaintStateMixin, NegotiationTenderState):
    cancellation_complaint_bid_owner_check = False
    cancellation_complaint_prolongs_award_complaint_periods = True
