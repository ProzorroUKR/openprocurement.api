from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU auction data",
)
class CFAUATenderAuctionResource(TenderAuctionResource):
    state_class = CFAUATenderState
