from openprocurement.tender.core.procedure.views.complaint_document import TenderComplaintDocumentResource
from openprocurement.tender.open.procedure.state.complaint_document import OpenComplaintDocumentState
from cornice.resource import resource


@resource(
    name="aboveThresholdUA.defense:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender complaint documents",
)
class OpenUADefenseComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = OpenComplaintDocumentState
