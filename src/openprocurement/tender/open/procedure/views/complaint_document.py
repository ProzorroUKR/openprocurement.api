from openprocurement.tender.core.procedure.views.complaint_document import TenderComplaintDocumentResource
from openprocurement.tender.open.procedure.state.complaint_document import OpenComplaintDocumentState
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_GROUP_NAME, ABOVE_THRESHOLD_GROUP
from cornice.resource import resource


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender complaint documents",
)
class OpenComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = OpenComplaintDocumentState
