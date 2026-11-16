from cornice.resource import resource

from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseTenderComplaintAppealDocumentResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender complaint appeal documents",
)
class ComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    pass
