from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.cfaua.procedure.state.complaint_document import (
    CFAUAComplaintDocumentState,
)
from openprocurement.tender.core.procedure.views.complaint_document import (
    TenderComplaintDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
    description="Tender complaint documents",
)
class CFAUAComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = CFAUAComplaintDocumentState
