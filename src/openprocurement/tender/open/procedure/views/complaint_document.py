from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.complaint_document import TenderComplaintDocumentResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.complaint_document import (
    AboveThresholdComplaintDocumentState,
    BelowThresholdComplaintDocumentState,
    COComplaintDocumentState,
    OpenTenderingComplaintDocumentState,
    RFPComplaintDocumentState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    description="Tender complaint documents",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenTenderComplaintDocumentResource(TenderComplaintDocumentResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdComplaintDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdComplaintDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdComplaintDocumentState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingComplaintDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: AboveThresholdComplaintDocumentState,
        ProcurementMethodType.SIMPLE_DEFENSE: AboveThresholdComplaintDocumentState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COComplaintDocumentState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdComplaintDocumentState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPComplaintDocumentState,
    }
