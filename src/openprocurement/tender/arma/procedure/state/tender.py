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
    alp_amount_key: str = "amountPercentage"
    awarding_criteria_key: str = "amountPercentage"

    @staticmethod
    def calc_tender_value(tender: dict) -> None:
        # disables calculation of lots[].value sum into tender.value, because ARMA does not have tender.value field
        pass

    @classmethod
    def set_weighted_value(cls, weighted_value, value_container, value_amount):
        weighted_value[cls.awarding_criteria_key] = round(value_amount, 2)
        return weighted_value
