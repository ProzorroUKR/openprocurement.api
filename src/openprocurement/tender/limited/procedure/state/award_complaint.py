from logging import getLogger

from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState

LOGGER = getLogger(__name__)


class NegotiationAwardComplaintState(AwardComplaintStateMixin, NegotiationTenderState):
    complaint_post_bid_owner_statuses = None
    create_allowed_tender_statuses = ("active",)
    update_allowed_tender_statuses = ("active",)
