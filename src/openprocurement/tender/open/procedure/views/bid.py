from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.bid import (
    AboveThresholdBidState,
    AboveThresholdEUBidState,
    AboveThresholdUABidState,
    BelowThresholdBidState,
    COBidState,
    DefenseBidState,
    OpenTenderingBidState,
    RFPBidState,
    SimpleDefenseBidState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    description="Tender bids",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenTenderBidResource(TenderBidResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdBidState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUABidState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUBidState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingBidState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseBidState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseBidState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COBidState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdBidState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPBidState,
    }
