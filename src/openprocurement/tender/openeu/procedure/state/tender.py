from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.openeu.procedure.models.award import Award


class BaseOpenEUTenderState(TenderState):
    award_class = Award
    active_bid_statuses = ("active", "pending")
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
