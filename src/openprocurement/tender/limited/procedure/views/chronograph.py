from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


@resource(
    name="negotiation:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    description="Tender chronograph",
)
class NegotiationChronographResource(TenderChronographResource):
    state_class = NegotiationTenderState


@resource(
    name="negotiation.quick:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    description="Tender chronograph",
)
class NegotiationQuickChronographResource(TenderChronographResource):
    state_class = NegotiationTenderState
