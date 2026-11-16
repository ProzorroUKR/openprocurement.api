from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.claim import (
    AboveThresholdEUTenderClaimState,
    AboveThresholdTenderClaimState,
    AboveThresholdUATenderClaimState,
    BelowThresholdTenderClaimState,
    COTenderClaimState,
    DefenseTenderClaimState,
    OpenTenderingTenderClaimState,
    RFPTenderClaimState,
    SimpleDefenseTenderClaimState,
)
from openprocurement.tender.open.procedure.state.complaint import (
    AboveThresholdEUTenderComplaintState,
    AboveThresholdTenderComplaintState,
    AboveThresholdUATenderComplaintState,
    COTenderComplaintState,
    DefenseTenderComplaintState,
    OpenTenderingTenderComplaintState,
    SimpleDefenseTenderComplaintState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    request_method=["GET"],
    description="Tender complaints get",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenBaseTenderComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    request_method=["PATCH"],
    complaintType="claim",
    description="Tender claims",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenTenderClaimResource(TenderClaimResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdTenderClaimState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUATenderClaimState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUTenderClaimState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingTenderClaimState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderClaimState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseTenderClaimState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COTenderClaimState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdTenderClaimState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPTenderClaimState,
    }


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
    ],
)
class OpenTenderComplaintResource(TenderComplaintResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdTenderComplaintState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUATenderComplaintState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUTenderComplaintState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingTenderComplaintState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderComplaintState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseTenderComplaintState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COTenderComplaintState,
    }
