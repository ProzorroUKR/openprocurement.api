from datetime import timedelta

from openprocurement.tender.arma.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import (
    TenderState as BaseTenderState,
)


class TenderState(BaseTenderState):
    award_class = Award
    active_bid_statuses = ("active", "pending")
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
    alp_due_date_period = timedelta(days=2)
