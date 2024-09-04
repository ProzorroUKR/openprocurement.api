from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.views.bid_sign import BidSignResource


@resource(
    name=f"{STAGE_2_EU_TYPE}:Tender Bid Sign",
    path="/tenders/{tender_id}/bids/{bid_id}/sign",
    description="Tender bid sign",
    procurementMethodType=STAGE_2_EU_TYPE,
)
class CompetitiveDialogueStage2EUBidSignResource(BidSignResource):
    pass


@resource(
    name=f"{STAGE_2_UA_TYPE}:Tender Bid Sign",
    path="/tenders/{tender_id}/bids/{bid_id}/sign",
    description="Tender bid sign",
    procurementMethodType=STAGE_2_UA_TYPE,
)
class CompetitiveDialogueStage2UABidSignResource(BidSignResource):
    pass
