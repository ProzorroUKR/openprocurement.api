from cornice.resource import resource

from openprocurement.tender.openuadefense.procedure.views.bid import (
    OpenUADefenseTenderBidResource,
)
from openprocurement.tender.simpledefense.procedure.state.bid import (
    SimpleDefenseBidState,
)


@resource(
    name="simple.defense:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="simple.defense",
    description="Tender simple.defense bids",
)
class SimpleDefenseTenderBidResource(OpenUADefenseTenderBidResource):
    state_class = SimpleDefenseBidState
