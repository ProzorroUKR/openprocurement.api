from openprocurement.tender.core.procedure.state.tender import TenderState


class NegotiationTenderState(TenderState):
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")

    def get_events(self, tender):
        yield from self.cancellation_events(tender)
        yield from self.complaint_events(tender)
        # there is no other events ...
