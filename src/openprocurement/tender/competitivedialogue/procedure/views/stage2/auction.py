from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.models.award import CDAward
from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.open.procedure.state.tender import AboveThresholdEUTenderState, AboveThresholdUATenderState


@resource(
    name="{}:Tender Auction".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue Stage 2 EU auction data",
)
class CompetitiveDialogueStage2EUAuctionResource(TenderAuctionResource):
    state_class = AboveThresholdEUTenderState
    award_class = CDAward


@resource(
    name="{}:Tender Auction".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue Stage 2 UA auction data",
)
class CompetitiveDialogueStage2UAAuctionResource(TenderAuctionResource):
    state_class = AboveThresholdUATenderState
    award_class = CDAward
