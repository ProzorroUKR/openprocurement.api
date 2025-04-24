from cornice.resource import resource

from openprocurement.tender.core.procedure.views.auction import (
    TenderAuctionResource as BaseTenderAuctionResource,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


@resource(
    name="requestForProposal:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="requestForProposal",
    description="Tender auction data",
)
class TenderAuctionResource(BaseTenderAuctionResource):
    state_class = RequestForProposalTenderState
