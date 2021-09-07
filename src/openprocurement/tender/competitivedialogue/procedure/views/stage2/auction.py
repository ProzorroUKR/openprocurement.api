from openprocurement.tender.core.procedure.awarding import add_next_award as add_award
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.models.award import Award
from openprocurement.tender.openeu.procedure.views.auction import EUTenderAuctionResource
from openprocurement.tender.openua.procedure.views.auction import UATenderAuctionResource
from cornice.resource import resource


@resource(
    name="{}:Tender Auction".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU auction data",
)
class CompetitiveDialogueStage2EUAuctionResource(EUTenderAuctionResource):
    def add_next_award(self):
        return add_award(self.request, award_class=Award)


@resource(
    name="{}:Tender Auction".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA auction data",
)
class CompetitiveDialogueStage2UAAuctionResource(UATenderAuctionResource):
    def add_next_award(self):
        return add_award(self.request, award_class=Award)
