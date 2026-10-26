from cornice.resource import resource

from openprocurement.tender.arma.constants import ARMA_PROCUREMENT_METHOD_TYPES, ARMA_ROUTE_PREFIX
from openprocurement.tender.core.procedure.views.complaint_document import (
    TenderComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.complaint_document import (
    AboveThresholdComplaintDocumentState,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender complaint documents",
)
class ComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = AboveThresholdComplaintDocumentState
