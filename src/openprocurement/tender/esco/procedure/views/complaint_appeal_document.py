from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseTenderComplaintAppealDocumentResource,
)
from openprocurement.tender.esco.constants import ESCO


@resource(
    name=f"{ESCO}:Tender Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=ESCO,
    description="Tender complaint appeal documents",
)
class ESCOComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    pass
