from cornice.resource import resource
from openprocurement.tender.openuadefense.procedure.views.auction import TenderAuctionResource


@resource(
    name="simple.defense:Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="simple.defense",
    description="Tender simple.defense auction data",
)
class TenderSimpleDefenseAuctionResource(TenderAuctionResource):
    pass
