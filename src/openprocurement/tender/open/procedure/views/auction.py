from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    BelowThresholdTenderState,
    COTenderState,
    OpenTenderingTenderState,
    RFPTenderState,
    SimpleDefenseTenderState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    description="Tender auction data",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenTenderAuctionResource(TenderAuctionResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdTenderState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUATenderState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUTenderState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingTenderState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: SimpleDefenseTenderState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseTenderState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COTenderState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdTenderState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPTenderState,
    }
