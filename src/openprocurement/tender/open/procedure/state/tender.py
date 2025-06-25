from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.open.procedure.models.award import Award


class OpenTenderState(TenderState):
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
    award_class = Award
