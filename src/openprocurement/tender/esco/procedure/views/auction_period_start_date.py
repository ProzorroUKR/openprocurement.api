from openprocurement.tender.openua.procedure.views.auction_period_start_date import UATenderAuctionPeriodResource
from cornice.resource import resource


@resource(
    name="esco:Tender Auction Period Start Date",
    collection_path="/tenders/{tender_id}/auctionPeriod",
    path="/tenders/{tender_id}/lots/{lot_id}/auctionPeriod",
    procurementMethodType="esco",
    description="Tender ESCO auctionPeriod start date",
)
class TenderAuctionPeriodResource(UATenderAuctionPeriodResource):
    pass
