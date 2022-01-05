from openprocurement.tender.core.procedure.views.auction_period_start_date import TenderAuctionPeriodResource
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Auction Period Start Date",
    collection_path="/tenders/{tender_id}/auctionPeriod",
    path="/tenders/{tender_id}/lots/{lot_id}/auctionPeriod",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU auctionPeriod start date",
)
class EUTenderAuctionPeriodResource(TenderAuctionPeriodResource):
    pass
