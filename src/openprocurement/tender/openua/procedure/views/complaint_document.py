from openprocurement.tender.core.procedure.views.complaint_document import TenderComplaintDocumentResource
from openprocurement.tender.open.procedure.state.complaint_document import OpenComplaintDocumentState
from cornice.resource import resource


@resource(
    name="aboveThresholdUA:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender complaint documents",
)
class OpenUAComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = OpenComplaintDocumentState
