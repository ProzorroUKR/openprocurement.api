from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState


class OpenUATenderState(TenderState):
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
    award_class = Award
