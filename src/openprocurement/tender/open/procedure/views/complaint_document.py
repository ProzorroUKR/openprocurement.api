from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_document import TenderComplaintDocumentResource
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
from openprocurement.tender.open.procedure.state.complaint_document import (
    AboveThresholdComplaintDocumentState,
    BelowThresholdComplaintDocumentState,
    COComplaintDocumentState,
    RFPComplaintDocumentState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    description="Tender complaint documents",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenTenderComplaintDocumentResource(TenderComplaintDocumentResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdComplaintDocumentState,
        ABOVE_THRESHOLD_UA: AboveThresholdComplaintDocumentState,
        ABOVE_THRESHOLD_EU: AboveThresholdComplaintDocumentState,
        ABOVE_THRESHOLD_UA_DEFENSE: AboveThresholdComplaintDocumentState,
        SIMPLE_DEFENSE: AboveThresholdComplaintDocumentState,
        COMPETITIVE_ORDERING: COComplaintDocumentState,
        BELOW_THRESHOLD: BelowThresholdComplaintDocumentState,
        REQUEST_FOR_PROPOSAL: RFPComplaintDocumentState,
    }
