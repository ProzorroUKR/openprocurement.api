from openprocurement.tender.competitiveordering.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState


class COTenderState(TenderState):
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
    award_class = Award
