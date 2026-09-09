from openprocurement.tender.core.procedure.state.tender import TenderState


class NegotiationTenderState(TenderState):
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
