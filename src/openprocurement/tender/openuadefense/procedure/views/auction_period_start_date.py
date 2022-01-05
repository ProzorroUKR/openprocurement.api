from openprocurement.tender.core.procedure.views.auction_period_start_date import TenderAuctionPeriodResource
from cornice.resource import resource


@resource(
    name="aboveThresholdUA.defense:Tender Auction Period Start Date",
    collection_path="/tenders/{tender_id}/auctionPeriod",
    path="/tenders/{tender_id}/lots/{lot_id}/auctionPeriod",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender UA.defense auctionPeriod start date",
)
class TenderAuctionPeriodResource(TenderAuctionPeriodResource):
    pass
