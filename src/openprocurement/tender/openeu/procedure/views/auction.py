from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU auction data",
)
class EUTenderAuctionResource(TenderAuctionResource):
    state_class = OpenEUTenderState
