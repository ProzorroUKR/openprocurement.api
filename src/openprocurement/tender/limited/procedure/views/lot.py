from cornice.resource import resource

from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.limited.procedure.state.lot import NegotiationLotState


@resource(
    name="negotiation.quick:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="negotiation.quick",
    description="Tender limited negotiation quick lots",
)
class TenderLimitedNegotiationQuickLotResource(TenderLotResource):
    state_class = NegotiationLotState


@resource(
    name="negotiation:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="negotiation",
    description="Tender limited negotiation lots",
)
class TenderLimitedNegotiationLotResource(TenderLimitedNegotiationQuickLotResource):
    pass
