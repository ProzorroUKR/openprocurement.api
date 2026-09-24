from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.models.award import CDAward
from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.open.procedure.state.tender import AboveThresholdEUTenderState, AboveThresholdUATenderState


@resource(
    name="{}:Tender Auction".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU auction data",
)
class CompetitiveDialogueStage2EUAuctionResource(TenderAuctionResource):
    state_class = AboveThresholdEUTenderState
    award_class = CDAward


@resource(
    name="{}:Tender Auction".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA auction data",
)
class CompetitiveDialogueStage2UAAuctionResource(TenderAuctionResource):
    state_class = AboveThresholdUATenderState
    award_class = CDAward
