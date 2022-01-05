from cornice.resource import resource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.openua.procedure.views.auction_period_start_date import UATenderAuctionPeriodResource
from openprocurement.tender.openeu.procedure.views.auction_period_start_date import EUTenderAuctionPeriodResource


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Auction Period Start Date",
    collection_path="/tenders/{tender_id}/auctionPeriod",
    path="/tenders/{tender_id}/lots/{lot_id}/auctionPeriod",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU Tender auctionPeriod start date",
)
class CompetitiveDialogueStage2EUTenderAuctionPeriodResource(EUTenderAuctionPeriodResource):
    pass


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Auction Period Start Date",
    collection_path="/tenders/{tender_id}/auctionPeriod",
    path="/tenders/{tender_id}/lots/{lot_id}/auctionPeriod",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA Tender auctionPeriod start date",
)
class CompetitiveDialogueStage2UATenderAuctionPeriodResource(UATenderAuctionPeriodResource):
    pass
