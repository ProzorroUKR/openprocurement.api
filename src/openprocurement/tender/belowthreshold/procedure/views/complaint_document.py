from openprocurement.tender.core.procedure.views.complaint_document import TenderComplaintDocumentResource
from openprocurement.tender.belowthreshold.procedure.state.complaint_document import BTComplaintDocumentState
from cornice.resource import resource


@resource(
    name="belowThreshold:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender complaint documents",
)
class BelowThresholdComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = BTComplaintDocumentState
