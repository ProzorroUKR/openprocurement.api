from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.openuadefense.procedure.state.tender import OpenUADefenseTenderState
from cornice.resource import resource


@resource(
    name="aboveThresholdUA.defense:Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender UA.defense auction data",
)
class TenderAuctionResource(TenderAuctionResource):
    state_class = OpenUADefenseTenderState
