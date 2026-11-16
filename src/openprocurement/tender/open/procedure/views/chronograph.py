from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.chronograph import TenderChronographResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    BelowThresholdTenderState,
    COTenderState,
    DefenseTenderState,
    OpenTenderingTenderState,
    RFPTenderState,
    SimpleDefenseTenderState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    description="Tender chronograph",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenTenderChronographResource(TenderChronographResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdTenderState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUATenderState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUTenderState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingTenderState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseTenderState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COTenderState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdTenderState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPTenderState,
    }
