from cornice.resource import resource

from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_PROCUREMENT_METHOD_TYPES,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.claim import (
    AboveThresholdEUTenderClaimState,
    AboveThresholdTenderClaimState,
    AboveThresholdUATenderClaimState,
    BelowThresholdTenderClaimState,
    COTenderClaimState,
    DefenseTenderClaimState,
    RFPTenderClaimState,
    SimpleDefenseTenderClaimState,
)
from openprocurement.tender.open.procedure.state.complaint import (
    AboveThresholdEUTenderComplaintState,
    AboveThresholdTenderComplaintState,
    AboveThresholdUATenderComplaintState,
    COTenderComplaintState,
    DefenseTenderComplaintState,
    SimpleDefenseTenderComplaintState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    request_method=["GET"],
    description="Tender complaints get",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
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
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenTenderClaimResource(TenderClaimResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdTenderClaimState,
        ABOVE_THRESHOLD_UA: AboveThresholdUATenderClaimState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUTenderClaimState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderClaimState,
        SIMPLE_DEFENSE: SimpleDefenseTenderClaimState,
        COMPETITIVE_ORDERING: COTenderClaimState,
        BELOW_THRESHOLD: BelowThresholdTenderClaimState,
        REQUEST_FOR_PROPOSAL: RFPTenderClaimState,
    }


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        ABOVE_THRESHOLD_UA_DEFENSE,
        SIMPLE_DEFENSE,
        COMPETITIVE_ORDERING,
    ],
)
class OpenTenderComplaintResource(TenderComplaintResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdTenderComplaintState,
        ABOVE_THRESHOLD_UA: AboveThresholdUATenderComplaintState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUTenderComplaintState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderComplaintState,
        SIMPLE_DEFENSE: SimpleDefenseTenderComplaintState,
        COMPETITIVE_ORDERING: COTenderComplaintState,
    }
