from openprocurement.tender.core.procedure.views.chronograph import TenderChronographResource
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState
from cornice.resource import resource


@resource(
    name="negotiation:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="negotiation",
    description="Tender chronograph",
)
class NegotiationChronographResource(TenderChronographResource):
    state_class = NegotiationTenderState


@resource(
    name="negotiation.quick:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="negotiation.quick",
    description="Tender chronograph",
)
class NegotiationQuickChronographResource(TenderChronographResource):
    state_class = NegotiationTenderState
