from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.openua.procedure.models.award import Award


class OpenUATenderState(TenderState):
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
    award_class = Award
