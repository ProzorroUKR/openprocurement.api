from datetime import timedelta

from openprocurement.tender.core.procedure.models.award import ARMAAward
from openprocurement.tender.core.procedure.state.tender import (
    TenderState as BaseTenderState,
)


class TenderState(BaseTenderState):
    award_class = ARMAAward
    active_bid_statuses = ("active", "pending")
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
    alp_due_date_period = timedelta(days=2)
    alp_amount_key: str = "amountPercentage"
    awarding_criteria_key: str = "amountPercentage"
    tender_value_from_lots = False  # ARMA does not have tender.value field
    weighted_value_with_currency = False
