from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules, dt_from_iso
from openprocurement.tender.core.procedure.state.award_complaint import AwardComplaintState
from openprocurement.tender.core.procedure.context import get_award, get_tender
from openprocurement.api.context import get_now
from openprocurement.api.validation import OPERATIONS
from logging import getLogger
from openprocurement.api.utils import raise_operation_error
from datetime import timedelta


LOGGER = getLogger(__name__)


class NegotiationAwardComplaintState(AwardComplaintState):
    tender_complaint_submit_time = timedelta(days=4)
    create_allowed_tender_statuses = ("active",)
    update_allowed_tender_statuses = ("active",)

