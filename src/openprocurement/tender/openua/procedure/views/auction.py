from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState
from cornice.resource import resource


@resource(
    name="aboveThresholdUA:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender UA auction data",
)
class UATenderAuctionResource(TenderAuctionResource):
    state_class = OpenUATenderState
