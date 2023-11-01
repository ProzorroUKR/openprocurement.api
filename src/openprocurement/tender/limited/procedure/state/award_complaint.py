from logging import getLogger
from datetime import timedelta
from openprocurement.tender.core.procedure.state.award_complaint import AwardComplaintStateMixin
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState

LOGGER = getLogger(__name__)


class NegotiationAwardComplaintState(AwardComplaintStateMixin, NegotiationTenderState):
    tender_complaint_submit_time = timedelta(days=4)
    create_allowed_tender_statuses = ("active",)
    update_allowed_tender_statuses = ("active",)

