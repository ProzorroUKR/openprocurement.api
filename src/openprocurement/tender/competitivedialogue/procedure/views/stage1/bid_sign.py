from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.serializers.bid import (
    BidSerializer,
)
from openprocurement.tender.core.procedure.views.bid_sign import BidSignResource


@resource(
    name=f"{CD_UA_TYPE}:Tender Bid Sign",
    path="/tenders/{tender_id}/bids/{bid_id}/sign",
    description="Tender bid sign",
    procurementMethodType=CD_UA_TYPE,
)
class CompetitiveDialogueUABidSignResource(BidSignResource):
    serializer_class = BidSerializer


@resource(
    name=f"{CD_EU_TYPE}:Tender Bid Sign",
    path="/tenders/{tender_id}/bids/{bid_id}/sign",
    description="Tender bid sign",
    procurementMethodType=CD_EU_TYPE,
)
class CompetitiveDialogueEUBidSignResource(BidSignResource):
    serializer_class = BidSerializer
